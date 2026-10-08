"""Batch runner for deterministic no-press LLM harness games."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int
from .llm_harness import NoPressLLMGameConfig, run_no_press_llm_game
from .llm_harness_batch_config import (
    NoPressLLMBatchConfig,
    load_no_press_llm_batch_config,
)
from .llm_harness_batch_config_snapshot import batch_config_snapshot
from .llm_harness_batch_summary import summarize_no_press_llm_results


def run_no_press_llm_batch(config: NoPressLLMBatchConfig) -> dict[str, Any]:
    validate_batch_config(config)
    games = [
        run_no_press_llm_game(game_config(config, index))
        for index in range(config.runs)
    ]
    results = [compact_game(game) for game in games]
    seat_config = games[0]["seat_config"]
    return {
        "mode": "table",
        "players": config.players,
        "seed_start": config.seed_start,
        "runs": config.runs,
        "max_turns": config.max_turns,
        "config": batch_config_snapshot(config),
        "seat_config": seat_config,
        "results": results,
        "summary": summarize_no_press_llm_results(results, seat_config),
        "games": games,
    }


def game_config(config: NoPressLLMBatchConfig, index: int) -> NoPressLLMGameConfig:
    return NoPressLLMGameConfig(
        players=config.players,
        seed=config.seed_start + index,
        seats=config.seats,
        max_turns=config.max_turns,
        variant_id=config.variant_id,
    )


def validate_batch_config(config: NoPressLLMBatchConfig) -> None:
    if not is_strict_int(config.runs) or config.runs < 1:
        raise ValueError("LLM experiment runs must be a positive integer")
    if not is_strict_int(config.seed_start):
        raise ValueError("LLM experiment seed_start must be an integer")


def compact_game(game: dict[str, Any]) -> dict[str, Any]:
    replay = game["replay"]
    summary = game["summary"]
    compact = {
        "seed": replay["seed"],
        "winner": replay["winner"],
        "turns": replay["turns"],
        "termination_reason": replay["termination_reason"],
        "elimination_order": summary["elimination_order"],
        "win_loss": summary["win_loss"],
        "invalid_action_count": summary["invalid_action_count"],
        "retry_count": summary["retry_count"],
        "trace_count": summary["trace_count"],
        "player_decision_metrics": summary["player_decision_metrics"],
    }
    for field in ("provider_latency_ms", "provider_cost"):
        if field in summary:
            compact[field] = summary[field]
    return compact


__all__ = [
    "NoPressLLMBatchConfig",
    "load_no_press_llm_batch_config",
    "run_no_press_llm_batch",
]
