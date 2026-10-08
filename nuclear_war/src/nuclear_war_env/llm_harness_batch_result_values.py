"""Expected compact result values for no-press LLM batch validation."""

from __future__ import annotations

from typing import Any

from .llm_harness_decision_metrics import player_decision_metrics
from .llm_harness_provider_metrics import provider_metrics_from_traces


def expected_no_press_llm_result_values(
    replay: dict[str, Any],
    trace: dict[str, Any],
) -> dict[str, Any]:
    expected = {
        "seed": replay["seed"],
        "winner": replay["winner"],
        "turns": replay["turns"],
        "termination_reason": replay["termination_reason"],
        "elimination_order": replay["eliminations"],
        "win_loss": _win_loss(replay),
        "invalid_action_count": sum(
            len(item["validation_errors"]) for item in trace["traces"]
        ),
        "retry_count": sum(int(item["retries"]) for item in trace["traces"]),
        "trace_count": len(trace["traces"]),
        "player_decision_metrics": player_decision_metrics(
            replay["final_populations"], trace["traces"]
        ),
    }
    expected.update(provider_metrics_from_traces(trace["traces"]))
    return expected


def _win_loss(replay: dict[str, Any]) -> dict[str, str]:
    winner = replay["winner"]
    if winner is None:
        return {player_id: "draw" for player_id in replay["final_populations"]}
    return {
        player_id: "win" if player_id == winner else "loss"
        for player_id in replay["final_populations"]
    }


__all__ = ["expected_no_press_llm_result_values"]
