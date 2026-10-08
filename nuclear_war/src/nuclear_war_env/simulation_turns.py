"""Simulation turn-order helpers."""

from __future__ import annotations

from collections.abc import Iterator

from .state import GameState


def turn_player_ids(state: GameState) -> Iterator[str]:
    """Yield each player once per round in clockwise order.

    An anti-missile interception sets ``state.next_player_id``; the interceptor
    then takes the next turn (re-anchoring clockwise play from them) but no living
    player is ever skipped or given a second turn within the round. After the round
    the clockwise anchor advances to the player after the last one to act.
    """
    order = list(state.players)
    if not order:
        return
    pending = set(order)
    last = _start_player(state, order)
    just_yielded: str | None = None
    while pending:
        nxt = _next_player(state, order, pending, just_yielded, last)
        if nxt is None:
            break
        pending.discard(nxt)
        just_yielded = nxt
        yield nxt
    if just_yielded is not None:
        state.current_player_id = order[(order.index(just_yielded) + 1) % len(order)]


def _start_player(state: GameState, order: list[str]) -> str:
    current = state.current_player_id
    if current is not None and current in order:
        return current
    return order[0]


def _next_player(
    state: GameState,
    order: list[str],
    pending: set[str],
    just_yielded: str | None,
    anchor: str,
) -> str | None:
    override = state.next_player_id
    state.next_player_id = None
    if override in pending:
        return override
    if just_yielded is None:
        return (
            anchor if anchor in pending else _clockwise_pending(order, anchor, pending)
        )
    return _clockwise_pending(order, just_yielded, pending)


def _clockwise_pending(
    order: list[str],
    start: str,
    pending: set[str],
) -> str | None:
    size = len(order)
    start_index = order.index(start)
    for step in range(1, size + 1):
        candidate = order[(start_index + step) % size]
        if candidate in pending:
            return candidate
    return None


__all__ = ["turn_player_ids"]
