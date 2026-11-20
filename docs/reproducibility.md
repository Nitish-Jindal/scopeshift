# Reproducibility

Use the existing isolated Cloud checkout; create no worktree unless requested.
Honor the current task's selected ref rather than automatically switching branches.
Python is pinned to 3.12.16; `uv.lock` fixes dependencies. The generated dataset is
versioned. `test_dataset_is_reproducible` compares it with the generator's complete
output. Wheels include dataset and independently labelled fixtures. `uv build`
checks installation artifacts; all ordinary workflows are credential-free.

In the managed Cloud machine, writable configuration paths are required:

```bash
export UV_PYTHON_INSTALL_DIR=/workspace/.scopeshift-tools/python
export UV_CACHE_DIR=/workspace/.scopeshift-tools/cache
export MPLCONFIGDIR=/workspace/.scopeshift-tools/matplotlib
uv sync --locked
```

The Inspect adapter sets writable XDG data/cache defaults within its chosen output
area when the caller has not supplied them. Offline fixtures explicitly provide
synthetic token-usage metadata; they do not download tokenizer files or claim
live usage. Real providers need their own configured dependencies and authorized
credentials; no such access is needed or used by tests.

## Containers behind a managed TLS proxy

The standard Compose build works with public registry/PyPI trust. Cloud's managed
TLS proxy can require the machine's public CA bundle inside the build. The
Dockerfile supports an optional ephemeral BuildKit CA mount:

```bash
docker build --secret id=build_ca,src=/etc/ssl/certs/ca-certificates.crt \
  -t scopeshift:local .
docker compose run --rm verify
docker compose run --rm demo
```

This mounts a public trust bundle during installation only. It is not a model
credential and is not copied into the image or repository. TLS and locked-artifact
hash verification stay enabled. No insecure transport flags are used. Runtime
containers run with no network, including the Inspect fixture tests.

## Experiment artifacts

A benchmark directory contains full per-trial evidence, ignored SQLite databases,
`summary.json` and `raw.jsonl.gz`. The compact gzip contains complete scenarios,
transport/configuration/seed, responses, wall times, grades and trusted evidence,
allowing independent regrading. `results/` retains a reviewed compact run plus
reliability summaries. Large transient run directories remain under ignored
`artifacts/`. Timings and concurrent winners can vary; serial semantic evidence
and all safety checks must reproduce. Never label fixture runs as live inference.

Budgets are explicit: deterministic corpus 180 trials, bounded exploration at most
54 combinations in the current grammar (budget flag 1..500), and Hypothesis settings
reported in its JSON. Stateful prefix counts include shrinking/re-execution and
must not be compared as independent completed trials. Seed 20261120 reproduces
this campaign with the locked Hypothesis version. A minimized three-command C3
history is retained as a regression fixture and can be replayed without Hypothesis.

## Evidence compatibility after independent review

Current exports use event/envelope schema 2. Regrading production evidence requires
the externally selected scenario and mode, for example
`grade(row["evidence"], scenario=row["scenario"], mode="host-fixed-v2")`. Stateful
grading additionally requires the trusted command list. Historical schema-1 raw
exports from commit 18c50d4 are intentionally rejected, not silently promoted to
current verified results. Rerun the benchmark/CLI to generate current evidence.
