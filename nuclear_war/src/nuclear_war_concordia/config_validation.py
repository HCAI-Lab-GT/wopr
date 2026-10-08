"""Validation for parsed Concordia harness configuration."""

from __future__ import annotations

from collections.abc import Mapping

from nuclear_war_env.players import player_ids

from .config_constants import AGENTS, AUTHORITY_AGENTS, HTTP_AGENTS, RUNTIMES
from .config_types import ConcordiaNoPressConfig, ConcordiaSeatConfig


def validate_config(config: ConcordiaNoPressConfig) -> None:
    if config.players != 4:
        raise ValueError("Concordia config players must be exactly 4")
    if config.max_turns < 1:
        raise ValueError("Concordia config max_turns must be positive")
    if config.runtime not in RUNTIMES:
        allowed = sorted(RUNTIMES)
        raise ValueError(f"Concordia config runtime must be one of {allowed}")
    _validate_seat_ids(config)
    _validate_seat_agents(config.seats)


def _validate_seat_ids(config: ConcordiaNoPressConfig) -> None:
    expected = set(player_ids(config.players))
    actual = set(config.seats)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            f"Concordia seats must match players: missing={missing}, extra={extra}"
        )


def _validate_seat_agents(seats: Mapping[str, ConcordiaSeatConfig]) -> None:
    allowed = sorted(AGENTS)
    for player_id, seat in seats.items():
        context = f"Concordia seat {player_id}"
        if seat.agent not in AGENTS:
            raise ValueError(f"{context} agent must be one of {allowed}")
        if seat.scripted_responses and seat.agent != "concordia_scripted":
            raise ValueError(f"{context} scripted_responses invalid for agent")
        if seat.client is not None and seat.agent not in HTTP_AGENTS:
            raise ValueError(f"{context} client requires an HTTP agent")
        if seat.agent == "concordia_scripted" and not seat.scripted_responses:
            raise ValueError(f"{context} requires scripted_responses")
        if seat.agent in HTTP_AGENTS and seat.client is None:
            raise ValueError(f"{context} requires client")
        if seat.authority is not None and seat.agent not in AUTHORITY_AGENTS:
            allowed_authority_agents = sorted(AUTHORITY_AGENTS)
            raise ValueError(
                f"{context} authority requires an agent in {allowed_authority_agents}"
            )


__all__ = ["validate_config"]
