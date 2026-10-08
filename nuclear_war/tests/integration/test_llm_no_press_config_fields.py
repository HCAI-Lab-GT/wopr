"""No-press LLM config field validation tests."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from nuclear_war_env.llm_harness_batch import load_no_press_llm_batch_config


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (
            lambda payload: payload.__setitem__("unexpected", True),
            "config fields are invalid",
        ),
        (
            lambda payload: payload["seats"]["player_0"].__setitem__(
                "unexpected",
                True,
            ),
            "seat player_0 fields are invalid",
        ),
    ],
)
def test_llm_batch_config_rejects_unknown_fields(
    mutator: Callable[[dict[str, Any]], object],
    message: str,
) -> None:
    payload = _config_payload()
    mutator(payload)

    with pytest.raises(ValueError, match=message):
        load_no_press_llm_batch_config(payload)


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
