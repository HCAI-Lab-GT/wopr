"""No-press LLM batch config snapshot validation tests."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from nuclear_war_env.llm_harness_batch import load_no_press_llm_batch_config
from nuclear_war_env.llm_harness_batch_config_snapshot import (
    batch_config_snapshot,
    validate_batch_config_snapshot,
)


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda summary: summary.__setitem__("runs", 2), "runs does not match"),
        (
            lambda summary: summary["seat_config"].__setitem__("player_0", "random"),
            "seats do not match",
        ),
    ],
)
def test_llm_batch_config_snapshot_rejects_summary_mismatch(
    mutator: Callable[[dict[str, Any]], object],
    message: str,
) -> None:
    config = load_no_press_llm_batch_config(_config_payload())
    summary = _summary_for_config(config)
    mutator(summary)

    with pytest.raises(ValueError, match=message):
        validate_batch_config_snapshot(batch_config_snapshot(config), summary)


def test_llm_batch_config_snapshot_rejects_partial_snapshot() -> None:
    config = load_no_press_llm_batch_config(_config_payload())
    snapshot = batch_config_snapshot(config)
    del snapshot["seats"]["player_0"]["fallback"]

    with pytest.raises(ValueError, match="strict snapshot"):
        validate_batch_config_snapshot(snapshot, _summary_for_config(config))


def _summary_for_config(config: Any) -> dict[str, Any]:
    return {
        "players": config.players,
        "seed_start": config.seed_start,
        "runs": config.runs,
        "max_turns": config.max_turns,
        "seat_config": {
            player_id: seat.agent for player_id, seat in config.seats.items()
        },
    }


def _config_payload() -> dict[str, Any]:
    return {
        "players": 4,
        "seed_start": 31,
        "runs": 1,
        "max_turns": 1,
        "seats": {
            "player_0": {
                "agent": "llm_scripted",
                "scripted_responses": ['{"action_id": "player_0:draw"}'],
            },
            "player_1": {"agent": "random"},
            "player_2": {"agent": "heuristic"},
            "player_3": {"agent": "decision_heuristic"},
        },
    }
