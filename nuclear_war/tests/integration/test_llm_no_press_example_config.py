"""No-press LLM example config tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.llm_harness_batch import (
    load_no_press_llm_batch_config,
    run_no_press_llm_batch,
)
from nuclear_war_env.llm_harness_batch_io import write_no_press_llm_batch

EXAMPLE_CONFIG = Path("docs/examples/no_press_llm_experiment.json")


def test_no_press_llm_example_config_runs_and_writes_artifacts(tmp_path) -> None:
    payload = json.loads(EXAMPLE_CONFIG.read_text(encoding="utf-8"))
    config = load_no_press_llm_batch_config(payload)

    result = run_no_press_llm_batch(config)
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)

    assert result["players"] == 4
    assert result["runs"] == 1
    assert result["max_turns"] == 3
    assert result["seat_config"] == {
        "player_0": "llm_first_legal",
        "player_1": "random",
        "player_2": "heuristic",
        "player_3": "decision_heuristic",
    }
    assert result["summary"]["total_trace_count"] >= 1
    assert (summary_path.parent / "seed-31.replay.json").is_file()
    assert (summary_path.parent / "seed-31.replay.traces.json").is_file()
