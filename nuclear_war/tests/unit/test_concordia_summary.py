"""Concordia no-press summary payload tests."""

from __future__ import annotations

from typing import Any

from nuclear_war_concordia.harness_payloads import summary


def test_summary_counts_fallback_used_traces() -> None:
    replay = _replay()
    traces = [
        _trace("player_0", fallback_used=True),
        _trace("player_1", fallback_used=False),
        _trace("player_2", fallback_used=True),
    ]

    result = summary(replay, traces, "concordia_style_fallback")

    assert result["fallback_count"] == 2


def test_summary_reports_zero_fallback_when_all_model_chosen() -> None:
    replay = _replay()
    traces = [
        _trace("player_0", fallback_used=False),
        _trace("player_1", fallback_used=False),
    ]

    result = summary(replay, traces, "concordia_style_fallback")

    assert result["fallback_count"] == 0


def test_summary_transient_retries_do_not_count_as_invalid_actions() -> None:
    replay = _replay()
    traces = [
        _trace("player_0", fallback_used=False, recoverable_provider_retries=2),
        _trace("player_1", fallback_used=False),
    ]

    result = summary(replay, traces, "concordia_style_fallback")

    assert result["invalid_action_count"] == 0
    assert result["recoverable_provider_retry_count"] == 2


def _replay() -> dict[str, Any]:
    return {
        "winner": "player_0",
        "turns": 3,
        "termination_reason": "one_player_remaining",
        "final_populations": {"player_0": 12, "player_1": 0, "player_2": 0},
    }


def _trace(
    player_id: str,
    *,
    fallback_used: bool,
    recoverable_provider_retries: int = 0,
) -> dict[str, Any]:
    return {
        "player_id": player_id,
        "validation_errors": [],
        "retries": 0,
        "fallback_used": fallback_used,
        "recoverable_provider_retries": recoverable_provider_retries,
    }
