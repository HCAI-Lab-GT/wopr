"""Privacy filter for full-press transcripts."""

from __future__ import annotations

from typing import Any


def visible_to(player: str, transcript: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [dict(message) for message in transcript if _is_visible_to(player, message)]


def _is_visible_to(player: str, message: dict[str, Any]) -> bool:
    if message.get("visibility") == "private":
        return player in {message.get("speaker"), message.get("recipient")}
    return True
