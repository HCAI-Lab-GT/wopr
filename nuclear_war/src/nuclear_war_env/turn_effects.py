"""Turn-control effects shared by actions and postal cards."""

from __future__ import annotations

from .state import PlayerState


def has_skip_turn(player: PlayerState) -> bool:
    return _skip_turn_count(player) > 0


def consume_skip_turn(player: PlayerState) -> bool:
    turns = _skip_turn_count(player)
    if turns <= 0:
        return False
    remaining = turns - 1
    if remaining:
        player.pending_orders["skip_turns"] = remaining
    else:
        player.pending_orders.pop("skip_turns", None)
    return True


def add_skip_turns(player: PlayerState, turns: int) -> None:
    if turns <= 0:
        return
    current = _skip_turn_count(player)
    player.pending_orders["skip_turns"] = current + turns


def _skip_turn_count(player: PlayerState) -> int:
    value = player.pending_orders.get("skip_turns", 0)
    if type(value) is int:
        return value
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    return 0


__all__ = ["add_skip_turns", "consume_skip_turn", "has_skip_turn"]
