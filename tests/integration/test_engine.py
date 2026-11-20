from pathlib import Path

import pytest

from scopeshift.dataset import load_dataset, select
from scopeshift.engine import replay, run, run_scenario
from scopeshift.oracle import grade


@pytest.mark.parametrize("scenario", load_dataset(), ids=lambda s: s.id)
@pytest.mark.parametrize("config", ["C0", "C2", "C3", "C4", "C5"])
def test_all_scenarios(scenario, config, tmp_path):
    result = run(scenario, config, tmp_path)
    assert result["grade"]["integrity"], result["grade"]
    if config == "C5":
        assert result["grade"]["outcome"] == "pass", result


@pytest.mark.parametrize(
    "config,scenario,safe",
    [
        ("C3", "revoke_after_gateway", False),
        ("C4", "revoke_after_recheck", False),
        ("C5", "revoke_after_recheck", True),
        ("C5", "authorized_update", True),
        ("C5", "unrelated_before_effect", True),
    ],
)
async def test_actual_mcp(config, scenario, safe, tmp_path):
    result = await run_scenario(select(scenario), config, tmp_path, transport="mcp")
    assert result["grade"]["integrity"]
    assert result["grade"]["effect_safety"] is safe


@pytest.mark.parametrize(
    "name",
    [
        "authorized_read",
        "authorized_search",
        "authorized_record_read",
        "authorized_message",
        "malicious_document",
    ],
)
async def test_mcp_tool_families(name, tmp_path):
    r = await run_scenario(select(name), "C5", tmp_path, transport="mcp")
    assert r["grade"]["outcome"] == "pass"


def test_replay_and_idempotent_revoked_retry(tmp_path):
    for config in ["C0", "C2", "C3", "C4", "C5"]:
        path = tmp_path / config
        r = run(select("retry_after_revocation"), config, path)
        assert r["responses"][0] == r["responses"][1]
        assert len(r["evidence"]["effects"]) == 1
        assert replay(path / "evidence.json", tmp_path / (config + "-replay"))["consistent"]


def test_c1_not_a_scripted_model_result(tmp_path):
    with pytest.raises(ValueError, match="model track"):
        run(select("authorized_update"), "C1", tmp_path)


def test_invalid_schedule(tmp_path):
    s = select("revoke_after_gateway")
    s.schedule[0].at = "inside_atomic_transaction"
    with pytest.raises(ValueError, match="checkpoint"):
        run(s, "C5", tmp_path)
    assert not Path(tmp_path / "run.sqlite3").exists()


def test_missing_evidence_fails_closed():
    assert grade({})["outcome"] == "invalid"


@pytest.mark.parametrize("config", ["C0", "C2", "C3", "C4", "C5"])
@pytest.mark.parametrize("name", ["approval_concurrent", "duplicate_concurrent"])
async def test_mcp_concurrent_barrier_variants(config, name, tmp_path):
    result = await run_scenario(select(name), config, tmp_path, transport="mcp")
    assert result["grade"]["integrity"], result["grade"]
    count = 1 if name == "duplicate_concurrent" or config == "C5" else 2
    assert result["grade"]["effect_count"] == count
    if name == "approval_concurrent":
        assert len(result["grade"]["unauthorized_effects"]) == count - 1
