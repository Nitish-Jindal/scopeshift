"""Credential-free deterministic workflows and an explicitly gated model track."""

import argparse
import json
import os
from pathlib import Path

from scopeshift.contracts import canonical
from scopeshift.dataset import select
from scopeshift.engine import replay, run
from scopeshift.experiments import benchmark, report
from scopeshift.exploration import explore
from scopeshift.fuzzing import campaign as fuzz
from scopeshift.fuzzing import replay_history
from scopeshift.mutations import campaign as mutate


def main(argv=None):
    parser = argparse.ArgumentParser(prog="scopeshift")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ["demo", "benchmark", "explore", "mutate", "fuzz"]:
        sub = commands.add_parser(name)
        sub.add_argument("--output", default=f"artifacts/{name}")
        if name in {"demo", "benchmark"}:
            sub.add_argument("--transport", choices=["native", "mcp"], default="mcp")
        if name == "benchmark":
            sub.add_argument("--seed", type=int, default=20261120)
            sub.add_argument("--limit", type=int)
        if name == "explore":
            sub.add_argument("--budget", type=int, default=60)
        if name == "fuzz":
            sub.add_argument("--config", choices=["C3", "C5"], default="C5")
            sub.add_argument("--seed", type=int, default=20261120)
            sub.add_argument("--examples", type=int, default=60)
            sub.add_argument("--steps", type=int, default=20)
    sub = commands.add_parser("replay")
    sub.add_argument("evidence")
    sub.add_argument("--output", default="artifacts/replay")
    sub = commands.add_parser("report")
    sub.add_argument("--input", default="artifacts/benchmark")
    sub.add_argument("--output", default="artifacts/report")
    sub = commands.add_parser("model")
    sub.add_argument("--scenario", default="authorized_update")
    sub.add_argument("--config", choices=[f"C{i}" for i in range(6)], default="C5")
    sub.add_argument("--model", required=True, help="Inspect model/provider identifier")
    sub.add_argument("--allow-live", action="store_true")
    sub.add_argument("--cost-limit", type=float, default=0.05)
    sub.add_argument("--output", default="artifacts/model")
    args = parser.parse_args(argv)
    os.environ.setdefault("MPLCONFIGDIR", str(Path("artifacts/.runtime/matplotlib").resolve()))
    if args.command == "demo":
        cases = [
            ("C3", "revoke_after_gateway"),
            ("C4", "revoke_after_recheck"),
            ("C5", "revoke_after_gateway"),
            ("C5", "authorized_update"),
            ("C5", "unrelated_before_effect"),
        ]
        result = []
        for config, name in cases:
            row = run(
                select(name),
                config,
                Path(args.output) / f"{config}-{name}",
                transport=args.transport,
            )
            result.append({"config": config, "scenario": name, "grade": row["grade"]})
        result = {
            "temporal_cases": result,
            "mutations": mutate(Path(args.output) / "mutations"),
            "stateful": fuzz(Path(args.output) / "stateful", config="C3", examples=100),
        }
    elif args.command == "benchmark":
        result = benchmark(args.output, transport=args.transport, seed=args.seed, limit=args.limit)
    elif args.command == "explore":
        result = explore(args.output, args.budget)
    elif args.command == "mutate":
        result = mutate(args.output)
    elif args.command == "fuzz":
        if not 1 <= args.examples <= 1000 or not 1 <= args.steps <= 100:
            parser.error("fuzz budget: examples 1..1000, steps 1..100")
        result = fuzz(
            args.output,
            config=args.config,
            seed_value=args.seed,
            examples=args.examples,
            steps=args.steps,
        )
    elif args.command == "replay":
        source = json.loads(Path(args.evidence).read_text())
        result = (
            replay_history(args.evidence)
            if "commands" in source
            else replay(args.evidence, args.output)
        )
    elif args.command == "report":
        result = report(args.input, args.output)
    else:
        if not args.model.startswith("mockllm/") and not args.allow_live:
            parser.error(
                "Live inference requires explicit --allow-live and paid API authorization."
            )
        if not 0 < args.cost_limit <= 1:
            parser.error("cost-limit must be within (0, 1] USD")
        from inspect_ai import eval

        from scopeshift.model_eval import model_task

        logs = eval(
            model_task(select(args.scenario), args.config, Path(args.output) / "runs"),
            model=args.model,
            log_dir=str(Path(args.output) / "logs"),
            cost_limit=args.cost_limit,
            display="none",
        )
        result = {
            "model": args.model,
            "statuses": [log.status for log in logs],
            "live": not args.model.startswith("mockllm/"),
        }
    if args.command in {"demo", "explore", "mutate"}:
        Path(args.output).mkdir(parents=True, exist_ok=True)
        (Path(args.output) / "summary.json").write_text(canonical(result) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
