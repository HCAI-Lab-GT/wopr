"""Experiment replay payload validation helpers."""

from __future__ import annotations

from typing import Any

from .agent_names import EXPERIMENT_AGENT_NAMES, reject_table_only_agent
from .experiment_replay_results import validate_experiment_results
from .experiment_summary_validation import validate_experiment_summary
from .integer_validation import is_strict_int

EXPERIMENT_FIELDS = (
    "mode",
    "players",
    "seed_start",
    "runs",
    "agent",
    "max_turns",
    "press",
    "results",
    "summary",
)


def validate_experiment_payload(payload: dict[str, Any]) -> None:
    _validate_batch_metadata(payload)
    validate_experiment_results(payload["results"], payload)
    validate_experiment_summary(payload["summary"], payload["results"])


def _validate_batch_metadata(payload: dict[str, Any]) -> None:
    mode = payload["mode"]
    agent = payload["agent"]
    players = payload["players"]
    press = payload["press"]
    if not isinstance(mode, str):
        raise ValueError("Experiment mode must be a string")
    if mode not in {"table", "postal"}:
        raise ValueError(f"Experiment has invalid mode: {mode}")
    if not isinstance(agent, str):
        raise ValueError("Experiment agent must be a string")
    if agent not in EXPERIMENT_AGENT_NAMES:
        raise ValueError(f"Experiment has invalid agent: {agent}")
    reject_table_only_agent(agent, mode, "Experiment")
    if not is_strict_int(players) or players < 2:
        raise ValueError(f"Experiment has invalid players: {players}")
    if press is not False:
        raise ValueError("Experiment press must be false for v1")


__all__ = ["EXPERIMENT_FIELDS", "validate_experiment_payload"]
