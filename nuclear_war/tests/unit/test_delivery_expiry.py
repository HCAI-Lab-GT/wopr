"""Delivery launch-track expiry: a delivery is only valid if the next face-up
card is a usable warhead (DELIV-001)."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.draw import resolve_face_up_card
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state() -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["player_0", "player_1"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards(
        [
            Card("missile", CardCategory.DELIVERY, "Missile", metadata={"capacity": 1}),
            Card(
                "prop",
                CardCategory.PROPAGANDA,
                "Propaganda 5M",
                value=5,
                metadata={"value_millions": 5},
            ),
            Card("warhead", CardCategory.WARHEAD, "Warhead 10 Mt", value=10),
        ]
    )
    return state


def _launches(player) -> dict:
    return player.pending_orders.get("launches", {})


def test_delivery_expires_when_next_face_up_is_not_a_warhead() -> None:
    state = _state()
    player = state.players["player_0"]

    resolve_face_up_card(state, player, None, "missile")
    assert "missile" in _launches(player)  # pending, awaiting a warhead

    # A non-warhead card the following turn means the delivery never armed: expire it.
    resolve_face_up_card(state, player, None, "prop")
    assert "missile" not in _launches(player)
    assert player.pending_orders.get("pending_delivery") is None

    # A warhead now has no pending delivery to load onto, so it is discarded.
    event = resolve_face_up_card(state, player, None, "warhead")
    assert event is not None
    assert event.event_type == "warhead_discarded"


def test_warhead_loads_onto_the_immediately_preceding_delivery() -> None:
    state = _state()
    player = state.players["player_0"]

    resolve_face_up_card(state, player, None, "missile")
    event = resolve_face_up_card(state, player, None, "warhead")

    assert event is not None
    assert event.event_type == "warhead_loaded"
    assert _launches(player)["missile"]["warheads"] == ["warhead"]
