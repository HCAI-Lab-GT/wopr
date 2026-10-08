"""Batch experiment runner for deterministic Nuclear War simulations."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any

from .agent_names import EXPERIMENT_AGENT_NAMES, reject_table_only_agent
from .integer_validation import is_strict_int
from .press import reject_press_mode
from .simulation import SimulationConfig, run_simulation
from .variant_catalog import validate_requested_variant
from .variants import ACTIVE_VARIANT_ID


@dataclass(frozen=True)
class ExperimentConfig:
    mode: str
    players: int
    seed_start: int
    runs: int
    agent: str
    max_turns: int = 50
    press: bool = False
    variant_id: str = ACTIVE_VARIANT_ID


def run_experiment(config: ExperimentConfig) -> dict[str, Any]:
    _validate_config(config)
    results = [
        _compact_result(
            run_simulation(
                SimulationConfig(
                    mode=config.mode,
                    players=config.players,
                    seed=config.seed_start + index,
                    agent=config.agent,
                    max_turns=config.max_turns,
                    press=config.press,
                    variant_id=config.variant_id,
                )
            )
        )
        for index in range(config.runs)
    ]
    return {
        "mode": config.mode,
        "players": config.players,
        "seed_start": config.seed_start,
        "runs": config.runs,
        "agent": config.agent,
        "max_turns": config.max_turns,
        "press": config.press,
        "results": results,
        "summary": _summarize(results),
    }


def _validate_config(config: ExperimentConfig) -> None:
    reject_press_mode(config.press)
    validate_requested_variant(config.variant_id, "Experiment")
    if not isinstance(config.mode, str):
        raise ValueError("Experiment mode must be a string")
    if config.mode not in {"table", "postal"}:
        raise ValueError(f"Unknown mode: {config.mode}")
    if not isinstance(config.agent, str):
        raise ValueError("Experiment agent must be a string")
    if config.agent not in EXPERIMENT_AGENT_NAMES:
        raise ValueError(f"Unknown agent: {config.agent}")
    reject_table_only_agent(config.agent, config.mode, "Experiment")
    if not is_strict_int(config.players):
        raise ValueError("Experiment players must be an integer")
    if config.players < 2:
        raise ValueError("At least two players are required")
    if not is_strict_int(config.seed_start):
        raise ValueError("Experiment seed_start must be an integer")
    if not is_strict_int(config.runs):
        raise ValueError("Experiment runs must be an integer")
    if config.runs < 1:
        raise ValueError("At least one run is required")
    if not is_strict_int(config.max_turns):
        raise ValueError("Experiment max_turns must be an integer")
    if config.max_turns < 1:
        raise ValueError("At least one turn is required")


def _compact_result(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "seed": payload["seed"],
        "mode": payload["mode"],
        "active_variant": payload["active_variant"],
        "agent": payload["agent"],
        "winner": payload["winner"],
        "turns": payload["turns"],
        "eliminations": payload["eliminations"],
        "final_populations": payload["final_populations"],
        "termination_reason": payload["termination_reason"],
        "pending_final_strikes": payload.get("pending_final_strikes", False),
    }


def _summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    turns = [int(result["turns"]) for result in results]
    eliminations = sum(len(result["eliminations"]) for result in results)
    return {
        "termination_counts": _counts(
            str(result["termination_reason"]) for result in results
        ),
        "winner_counts": _counts(_winner_key(result["winner"]) for result in results),
        "average_turns": sum(turns) / len(turns),
        "total_eliminations": eliminations,
    }


def _counts(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _winner_key(winner: Any) -> str:
    if winner is None:
        return "no_winner"
    return str(winner)


__all__ = ["ExperimentConfig", "run_experiment"]
