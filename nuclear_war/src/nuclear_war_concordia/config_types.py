"""Data types for Concordia harness configuration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from nuclear_war_agents import HTTPClientConfig
from nuclear_war_env.variants import ACTIVE_VARIANT_ID

from .authority_config import AuthorityConfig
from .press_config import PressConfig


@dataclass(frozen=True)
class ConcordiaSeatConfig:
    agent: str
    identity: Mapping[str, str]
    max_retries: int = 1
    scripted_responses: tuple[str, ...] = ()
    client: HTTPClientConfig | None = None
    authority: AuthorityConfig | None = None


@dataclass(frozen=True)
class ConcordiaNoPressConfig:
    players: int
    seed: int
    seats: Mapping[str, ConcordiaSeatConfig]
    max_turns: int = 50
    runtime: str = "auto"
    variant_id: str = ACTIVE_VARIANT_ID
    press: PressConfig = PressConfig()


__all__ = ["ConcordiaNoPressConfig", "ConcordiaSeatConfig"]
