"""Measured benchmark execution and compact reproducibility artifacts."""

import gzip
import importlib.metadata
import json
import platform
import sqlite3
import sys
from pathlib import Path

from scopeshift.contracts import canonical, digest
from scopeshift.dataset import load_dataset
from scopeshift.engine import run
from scopeshift.metrics import summarize


def package_version(name):
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None  # Development tools are optional in a runtime-only wheel install.


def benchmark(directory, *, transport="mcp", seed=20261120, limit=None):
    if limit is not None and limit < 1:
        raise ValueError("benchmark limit must be positive")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    dataset = load_dataset()
    results = []
    for config in ["C0", "C2", "C3", "C4", "C5"]:
        for scenario in dataset:
            if limit is not None and len(results) >= limit:
                break
            result = run(
                scenario,
                config,
                directory / "runs" / config / scenario.id,
                transport=transport,
                seed=seed,
            )
            results.append(result)
        if limit is not None and len(results) >= limit:
            break
    summary = {
        "schema_version": 1,
        "seed": seed,
        "transport": transport,
        "dataset_digest": digest([s.model_dump() for s in dataset]),
        "scenario_count": len(dataset),
        "executions": len(results),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "sqlite": sqlite3.sqlite_version,
        "versions": {
            p: package_version(p)
            for p in ["mcp", "inspect-ai", "pydantic", "hypothesis", "pytest", "ruff", "matplotlib"]
        },
        "metrics": summarize(results),
        "scope": "Fixed requests; C1 prompt compliance and live model tokens are not measured.",
    }
    (directory / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    raw = "".join(canonical(r) + "\n" for r in results).encode()
    (directory / "raw.jsonl.gz").write_bytes(gzip.compress(raw, mtime=0))
    return summary


def report(directory, destination):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    summary = json.loads((Path(directory) / "summary.json").read_text())
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    configs = list(summary["metrics"])
    values = [summary["metrics"][c]["unsafe_trial_rate"]["rate"] for c in configs]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(configs, values, color=["#ad4c38", "#d08532", "#cdab4d", "#54979b", "#226c49"])
    ax.set(
        ylabel="Trials with unauthorized committed effects / valid trials",
        ylim=(0, 1),
        title=f"ScopeShift: {summary['executions']} deterministic trials ({summary['transport']})",
    )
    for i, config in enumerate(configs):
        row = summary["metrics"][config]["unsafe_trial_rate"]
        ax.text(i, values[i] + 0.015, f"{row['numerator']}/{row['denominator']}", ha="center")
    fig.tight_layout()
    svg_path = destination / "effect-safety.svg"
    fig.savefig(svg_path)
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n"
    )
    plt.close(fig)
    lines = [
        "# ScopeShift measured results",
        "",
        f"Executed {summary['executions']} trials on {summary['scenario_count']} scenarios "
        f"using {summary['transport']}; seed {summary['seed']}.",
        "",
        "| Configuration | Unsafe trials | Unauthorized effects | "
        "Legitimate completion | Mean ms |",
        "|---|---:|---:|---:|---:|",
    ]
    for config, metrics in summary["metrics"].items():
        unsafe = metrics["unsafe_trial_rate"]
        effects = metrics["unauthorized_protected_effect_rate"]
        utility = metrics["legitimate_task_completion_rate"]
        lines.append(
            f"| {config} | {unsafe['numerator']}/{unsafe['denominator']} "
            f"| {effects['numerator']}/{effects['denominator']} "
            f"| {utility['numerator']}/{utility['denominator']} "
            f"| {metrics['latency_ms']['mean']:.2f} |"
        )
    lines += [
        "",
        "![Measured effect safety](effect-safety.svg)",
        "",
        "Raw evidence and exact metric denominators are retained with the benchmark summary. "
        "No live model inference was run. C1 requires the separate model track. "
        "Latency includes process/session startup for MCP and is descriptive, not a rigorous "
        "microbenchmark. Concurrent variants compare invariant outcomes; the winning request "
        "can vary. No confidence intervals are claimed for these fixed cases.",
    ]
    (destination / "measured-results.md").write_text("\n".join(lines) + "\n")
    return {"executions": summary["executions"], "report": str(destination / "measured-results.md")}
