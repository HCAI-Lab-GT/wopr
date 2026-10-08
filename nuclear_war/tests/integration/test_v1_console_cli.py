"""Console-script tests for Nuclear War v1 commands."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


def test_console_validate_rules_reports_ok() -> None:
    result = _run_console("validate-rules")

    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["active_variant"]["variant_id"] == "base_later_two_d10"


def test_console_experiment_replay_and_summarize(tmp_path) -> None:
    output = tmp_path / "batch.json"
    _run_console(
        "experiment",
        "--mode",
        "table",
        "--players",
        "2",
        "--seed-start",
        "3",
        "--runs",
        "2",
        "--agent",
        "random",
        "--max-turns",
        "5",
        "--out",
        str(output),
    )

    replay = _run_console("replay", str(output))
    summary = _run_console("summarize", str(output))
    replay_payload = json.loads(replay.stdout)
    summary_payload = json.loads(summary.stdout)
    assert replay_payload["runs"] == 2
    assert len(replay_payload["results"]) == 2
    assert summary_payload["runs"] == 2
    assert "summary" in summary_payload


def _run_console(*args: str | Path) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["nuclear-war", *(str(arg) for arg in args)],
        capture_output=True,
        check=False,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result
