"""Simulation config validation helpers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .agent_names import SIMULATION_AGENT_NAMES, reject_table_only_agent
from .integer_validation import is_strict_int
from .modes import VALID_MODES
from .press import reject_press_mode
from .variant_catalog import validate_requested_variant


def validate_simulation_config(
    mode: Any,
    players: Any,
    seed: Any,
    agent: Any,
    max_turns: Any,
    press: bool,
    variant_id: Any,
    allowed_agents: Sequence[str] = SIMULATION_AGENT_NAMES,
) -> None:
    # Defaults to the runnable single-agent names (fail-closed). The per-seat
    # decision-agent path passes REPLAY_AGENT_NAMES so it can label its replay
    # "mixed_seats" without that label leaking into single-agent runs.
    reject_press_mode(press)
    validate_requested_variant(variant_id, "Simulation")
    if not isinstance(mode, str):
        raise ValueError("Simulation mode must be a string")
    if mode not in VALID_MODES:
        raise ValueError(f"Unknown mode: {mode}")
    if not isinstance(agent, str):
        raise ValueError("Simulation agent must be a string")
    if agent not in allowed_agents:
        raise ValueError(f"Unknown agent: {agent}")
    reject_table_only_agent(agent, mode, "Simulation")
    if not is_strict_int(players):
        raise ValueError("Simulation players must be an integer")
    if players < 2:
        raise ValueError("At least two players are required")
    if not is_strict_int(seed):
        raise ValueError("Simulation seed must be an integer")
    if not is_strict_int(max_turns):
        raise ValueError("Simulation max_turns must be an integer")
    if max_turns < 1:
        raise ValueError("At least one turn is required")


__all__ = ["validate_simulation_config"]
