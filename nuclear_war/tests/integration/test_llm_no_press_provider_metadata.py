"""No-press LLM provider metadata tests."""

from __future__ import annotations

import json
from typing import Any, cast

import pytest

from nuclear_war_env.cli import main
from nuclear_war_env.llm_harness_batch import load_no_press_llm_batch_config
from nuclear_war_env.llm_trace_artifacts import read_trace_artifact
from nuclear_war_env.replay import read_replay


@pytest.mark.parametrize(
    "field",
    ["scripted_provider_latency_ms", "scripted_provider_cost"],
)
def test_llm_batch_config_rejects_extra_scripted_provider_metadata(
    field: str,
) -> None:
    payload = _config_payload()
    seats = cast(dict[str, dict[str, Any]], payload["seats"])
    seats["player_0"][field] = [1, 2, 3]

    with pytest.raises(ValueError, match=f"{field} must not exceed scripted_responses"):
        load_no_press_llm_batch_config(payload)


@pytest.mark.parametrize(
    ("agent", "field", "value"),
    [
        ("random", "scripted_responses", ['{"action_id": "player_1:draw"}']),
        ("llm_first_legal", "scripted_provider_latency_ms", [12]),
        ("heuristic", "scripted_provider_cost", [0.01]),
    ],
)
def test_llm_batch_config_rejects_scripted_fields_for_non_scripted_seats(
    agent: str,
    field: str,
    value: object,
) -> None:
    payload = _config_payload()
    seats = cast(dict[str, dict[str, Any]], payload["seats"])
    seats["player_1"] = {"agent": agent, field: value}

    with pytest.raises(ValueError, match=f"{field} requires llm_scripted agent"):
        load_no_press_llm_batch_config(payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [("max_retries", 2), ("fallback", "pass")],
)
def test_llm_batch_config_rejects_llm_controls_for_baseline_seats(
    field: str,
    value: object,
) -> None:
    payload = _config_payload()
    seats = cast(dict[str, dict[str, Any]], payload["seats"])
    seats["player_1"] = {"agent": "random", field: value}

    with pytest.raises(ValueError, match=f"{field} requires LLM seat"):
        load_no_press_llm_batch_config(payload)


def test_cli_llm_experiment_writes_provider_metadata_when_available(tmp_path) -> None:
    config_path = tmp_path / "llm_config.json"
    output_dir = tmp_path / "out"
    payload = _config_payload()
    seats = cast(dict[str, dict[str, Any]], payload["seats"])
    seats["player_0"]["scripted_provider_latency_ms"] = [23]
    seats["player_0"]["scripted_provider_cost"] = [0.007]
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    code = main(
        [
            "llm-experiment",
            "--config",
            str(config_path),
            "--out-dir",
            str(output_dir),
        ]
    )

    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    replay = read_replay(output_dir / "seed-31.replay.json")
    trace = read_trace_artifact(output_dir / "seed-31.replay.traces.json", replay)
    expected_latency = _sum_trace_field(trace, "provider_latency_ms")
    expected_cost = _sum_trace_field(trace, "provider_cost")
    assert code == 0
    assert summary["summary"]["total_provider_latency_ms"] == expected_latency
    assert summary["summary"]["total_provider_cost"] == pytest.approx(expected_cost)
    assert summary["results"][0]["provider_latency_ms"] == expected_latency
    assert summary["results"][0]["provider_cost"] == pytest.approx(expected_cost)


def _sum_trace_field(trace: dict[str, Any], field: str) -> float:
    return sum(item[field] for item in trace["traces"] if item[field] is not None)


def _config_payload() -> dict[str, object]:
    return {
        "players": 4,
        "seed_start": 31,
        "runs": 1,
        "max_turns": 1,
        "seats": {
            "player_0": {
                "agent": "llm_scripted",
                "scripted_responses": ["not-json", '{"action_id": "player_0:draw"}'],
            },
            "player_1": {"agent": "random"},
            "player_2": {"agent": "heuristic"},
            "player_3": {"agent": "decision_heuristic"},
        },
    }
