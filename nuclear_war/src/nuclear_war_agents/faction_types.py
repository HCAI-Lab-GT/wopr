"""Shared types for faction C2 collective decision agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SubordinateVote:
    member_id: str
    action_id: str
    rationale: str | None = None


@dataclass(frozen=True)
class FactionDeliberation:
    archetype: str
    member_votes: list[SubordinateVote]
    selected_action_id: str
    rule: str
    parameters: dict[str, Any] = field(default_factory=dict)
    player_id: str = ""
    turn: int = 0
    decision_type: str = "none"


@dataclass(frozen=True)
class FactionConfig:
    archetype: str
    parameters: dict[str, Any] = field(default_factory=dict)


__all__ = ["FactionConfig", "FactionDeliberation", "SubordinateVote"]
