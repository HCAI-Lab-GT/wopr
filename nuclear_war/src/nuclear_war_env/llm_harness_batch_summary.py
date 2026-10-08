"""Summary helpers for no-press LLM harness batches."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .llm_harness_decision_metrics import agent_decision_metrics
from .llm_harness_provider_metrics import provider_totals_from_results

OUTCOME_KEYS = ("win", "loss", "draw")


def summarize_no_press_llm_results(
    results: list[dict[str, Any]],
    seat_config: dict[str, str],
) -> dict[str, Any]:
    turns = [int(result["turns"]) for result in results]
    summary = {
        "runs": len(results),
        "agent_outcomes": _agent_outcomes(results, seat_config),
        "agent_decision_metrics": agent_decision_metrics(results, seat_config),
        "winner_counts": _counts(_winner_key(result["winner"]) for result in results),
        "termination_counts": _counts(
            str(result["termination_reason"]) for result in results
        ),
        "average_turns": sum(turns) / len(turns),
        "total_eliminations": sum(
            len(result["elimination_order"]) for result in results
        ),
        "total_invalid_action_count": sum(
            int(result["invalid_action_count"]) for result in results
        ),
        "total_retry_count": sum(int(result["retry_count"]) for result in results),
        "total_trace_count": sum(int(result["trace_count"]) for result in results),
    }
    summary.update(provider_totals_from_results(results))
    return summary


def _agent_outcomes(
    results: list[dict[str, Any]],
    seat_config: dict[str, str],
) -> dict[str, dict[str, int]]:
    counters: dict[str, Counter[str]] = {}
    for result in results:
        for player_id, outcome in result["win_loss"].items():
            agent = seat_config[str(player_id)]
            counters.setdefault(agent, Counter())[str(outcome)] += 1
    return {
        agent: {outcome: counter.get(outcome, 0) for outcome in OUTCOME_KEYS}
        for agent, counter in sorted(counters.items())
    }


def _counts(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _winner_key(winner: Any) -> str:
    return "no_winner" if winner is None else str(winner)


__all__ = ["summarize_no_press_llm_results"]
