"""Delivery and warhead compatibility tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.cards_registry import (
    CardType,
    card_from_record,
    load_card_registry,
)
from nuclear_war_env.engine.draw import advance_queue, set_face_down_cards
from nuclear_war_env.rules import RULES_PATH
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state(cards: list[Card]) -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards(cards)
    return state


def _first_card(card_type: CardType, name: str) -> Card:
    registry = load_card_registry(RULES_PATH)
    for record in registry.values():
        if record.type is card_type and record.name == name:
            return card_from_record(record)
    raise AssertionError(f"Missing registry card: {name}")


def test_delivery_rejects_oversized_registry_warhead() -> None:
    delivery = _first_card(CardType.CARRIER, "Polaris Missile")
    warhead = _first_card(CardType.WARHEAD, "Warhead 20 Mt")
    state = _state([delivery, warhead])
    player = state.players["p1"]
    player.hand = [delivery.identifier, warhead.identifier]
    set_face_down_cards(player, [delivery.identifier, warhead.identifier])
    first = advance_queue(state, player)
    second = advance_queue(state, player)
    assert first is not None
    assert first.event_type == "delivery_ready"
    assert second is not None
    assert second.event_type == "warhead_discarded"
    # The oversized warhead is not usable, so the delivery's window is spent and it
    # is discarded (it does not linger waiting for a later compatible warhead).
    assert delivery.identifier not in player.pending_orders.get("launches", {})


def test_bomber_loads_multiple_registry_warheads_within_payload() -> None:
    delivery = _first_card(CardType.CARRIER, "B-70 Bomber")
    warhead = _first_card(CardType.WARHEAD, "Warhead 10 Mt")
    state = _state([delivery, warhead])
    player = state.players["p1"]
    player.hand = [delivery.identifier, warhead.identifier]
    set_face_down_cards(player, [delivery.identifier, warhead.identifier])
    advance_queue(state, player)
    advance_queue(state, player)
    player.hand = [warhead.identifier]
    set_face_down_cards(player, [warhead.identifier])
    event = advance_queue(state, player)
    launch = player.pending_orders["launches"][delivery.identifier]
    assert event is not None
    assert event.event_type == "warhead_loaded"
    assert launch["warheads"] == [warhead.identifier, warhead.identifier]


def test_delivery_rejects_float_capacity_metadata() -> None:
    delivery = Card(
        "delivery",
        CardCategory.DELIVERY,
        "Delivery",
        metadata={"capacity": 1.0},
    )
    warhead = Card("warhead", CardCategory.WARHEAD, "Warhead", value=10)
    state = _state([delivery, warhead])
    player = state.players["p1"]
    player.hand = [delivery.identifier, warhead.identifier]
    set_face_down_cards(player, [delivery.identifier, warhead.identifier])
    advance_queue(state, player)

    event = advance_queue(state, player)

    assert event is not None
    assert event.event_type == "warhead_discarded"
    # Capacity-0 delivery cannot take the warhead, so its window is spent.
    assert delivery.identifier not in player.pending_orders.get("launches", {})
