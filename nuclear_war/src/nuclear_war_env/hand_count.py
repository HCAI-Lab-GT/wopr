"""Card-count helpers for draw-limit accounting."""

from __future__ import annotations

from .state import PlayerState


def draw_count(player: PlayerState) -> int:
    face_down = sum(1 for card_id in player.face_down_queue if card_id is not None)
    deterrents = sum(1 for card_id in player.deterrents if card_id is not None)
    return len(player.hand) + face_down + deterrents


__all__ = ["draw_count"]
