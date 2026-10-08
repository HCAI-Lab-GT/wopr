"""Draw and queue management helpers."""

from __future__ import annotations

from collections.abc import Iterable

from nuclear_war_env.card_kinds import is_secret_like
from nuclear_war_env.cards import CardCategory
from nuclear_war_env.engine.launch_helpers import (
    _is_bomber,
    can_load_warhead,
    delivery_capacity,
)
from nuclear_war_env.hand_count import draw_count
from nuclear_war_env.state import HAND_LIMIT, GameState, PlayerState

from .events import DrawLimitReached, EngineEvent


def draw_phase(state: GameState, player_id: str) -> list[EngineEvent]:
    player = state.players[player_id]
    events: list[EngineEvent] = []
    safety_counter = 0
    while draw_count(player) < HAND_LIMIT:
        safety_counter += 1
        if safety_counter > HAND_LIMIT * 2:
            raise DrawLimitReached("Unable to reach hand limit; deck likely exhausted")
        if (
            not state.draw_pile
            and state.discard_pile
            and all(is_secret_like(card.category) for card in state.discard_pile)
        ):
            break
        try:
            card = state.draw_card()
        except ValueError:
            break
        events.append(EngineEvent("card_drawn", player_id, card.identifier))
        if is_secret_like(card.category):
            player.secrets.append(card.identifier)
            state.discard(card)
            events.append(EngineEvent("secret_queued", player_id, card.identifier))
            continue
        player.hand.append(card.identifier)
    return events


def set_face_down_cards(player: PlayerState, card_ids: Iterable[str]) -> None:
    queue = list(player.face_down_queue)
    card_list = list(card_ids)
    for i in range(len(queue)):
        if queue[i] is None and card_list:
            card_id = card_list.pop(0)
            if card_id is not None and _remove_placeable_card(player, card_id):
                queue[i] = card_id
    player.face_down_queue.clear()
    player.face_down_queue.extend(queue)


def _remove_placeable_card(player: PlayerState, card_id: str) -> bool:
    if card_id in player.hand:
        player.hand.remove(card_id)
        return True
    for index, deterrent_id in enumerate(player.deterrents):
        if deterrent_id == card_id:
            player.deterrents[index] = None
            return True
    return False


def advance_queue(state: GameState, player: PlayerState) -> EngineEvent | None:
    previous = player.face_up
    player.advance_face_down()
    if player.face_up is None:
        return None
    face_up = player.face_up
    return resolve_face_up_card(state, player, previous, face_up)


def resolve_face_up_card(
    state: GameState,
    player: PlayerState,
    previous: str | None,
    face_up: str | None = None,
) -> EngineEvent | None:
    card_id = face_up or player.face_up
    if card_id is None:
        return None
    card = state.card_by_id(card_id)
    launches = player.pending_orders.setdefault("launches", {})

    if card.category is CardCategory.WARHEAD:
        # A warhead may only arm the delivery that was face-up immediately before it.
        pending_id = player.pending_orders.get("pending_delivery")
        if (
            pending_id is not None
            and pending_id in launches
            and can_load_warhead(state, pending_id, launches[pending_id], card)
        ):
            launches[pending_id]["warheads"].append(card.identifier)
            # A bomber keeps accepting warheads across turns until its payload is
            # exhausted or a non-warhead card spends it; a single-shot delivery is
            # now armed and no longer pending.
            if not _is_bomber(state.card_by_id(pending_id)):
                player.pending_orders["pending_delivery"] = None
            player.face_up = None
            return EngineEvent(
                "warhead_loaded",
                player.player_id,
                card.identifier,
                {"delivery": pending_id, "previous": previous},
            )
        _expire_pending_delivery(state, player)
        state.discard(card)
        player.face_up = None
        return EngineEvent(
            "warhead_discarded",
            player.player_id,
            card.identifier,
            {"reason": "no_delivery", "previous": previous},
        )

    # Any non-warhead resolution means a pending delivery never received its warhead.
    _expire_pending_delivery(state, player)

    if card.category is CardCategory.DELIVERY:
        capacity = delivery_capacity(card)
        launches[card.identifier] = {
            "delivery": card.identifier,
            "capacity": capacity,
            "warheads": [],
            "target": None,
        }
        player.pending_orders["pending_delivery"] = card.identifier
        player.face_up = None
        return EngineEvent(
            "delivery_ready",
            player.player_id,
            card.identifier,
            {"capacity": capacity, "previous": previous},
        )
    if card.category is CardCategory.PROPAGANDA:
        propaganda = player.pending_orders.setdefault("propaganda", [])
        propaganda.append(card.identifier)
        player.face_up = None
        state.discard(card)
        return EngineEvent(
            "propaganda_ready",
            player.player_id,
            card.identifier,
            {"previous": previous},
        )
    # Anti-missiles are reactive hand cards: one resolved on the launch track is
    # wasted and simply discarded (interception is played from hand, see
    # launch_helpers.attempt_intercept). All other cards resolve to a plain discard.
    player.face_up = None
    state.discard(card)
    return EngineEvent(
        "card_resolved",
        player.player_id,
        card.identifier,
        {"previous": previous},
    )


def _expire_pending_delivery(state: GameState, player: PlayerState) -> None:
    """Discard a face-up delivery that never received its warhead in time.

    The launch track holds one pending (un-armed) delivery; once the following
    face-up card is not a usable warhead the delivery is spent and leaves play.
    """
    pending_id = player.pending_orders.get("pending_delivery")
    if pending_id is None:
        return
    launches = player.pending_orders.get("launches", {})
    launch = launches.get(pending_id)
    if launch is not None and not launch.get("warheads"):
        state.discard(state.card_by_id(pending_id))
        launches.pop(pending_id, None)
    player.pending_orders["pending_delivery"] = None


__all__ = [
    "draw_phase",
    "set_face_down_cards",
    "advance_queue",
    "resolve_face_up_card",
]
