"""Event models shared across engine routines."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class EngineEvent:
    event_type: str
    player_id: str | None
    card_id: str | None = None
    payload: dict[str, object] = field(default_factory=dict)


class DrawLimitReached(RuntimeError):
    """Raised when the hand limit cannot be satisfied due to deck exhaustion."""


__all__ = ["EngineEvent", "DrawLimitReached"]
