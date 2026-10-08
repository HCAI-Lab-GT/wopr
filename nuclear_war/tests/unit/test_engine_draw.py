"""Draw and queue engine tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import advance_queue, draw_phase, set_face_down_cards
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import (
    FACE_DOWN_SLOTS,
    GameState,
    PlayerState,
    Ruleset,
    create_players,
)


def _card(identifier: str, category: CardCategory = CardCategory.WARHEAD) -> Card:
    return Card(identifier=identifier, category=category, name=identifier)


def _build_state(cards: list[Card]) -> GameState:
    players = create_players(["p1"], starting_population=10)
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=players,
        draw_pile=list(cards),
        rng=SeededRNG(seed=1),
    )
    state.register_cards(cards)
    return state


def test_draw_phase_adds_cards_until_limit() -> None:
    deck = [_card(f"c{i}") for i in range(10)]
    state = _build_state(deck)
    player = state.players["p1"]
    player.hand = []
    events = draw_phase(state, "p1")
    assert len(player.hand) == 10
    assert len(events) == 10


def test_draw_phase_counts_face_down_cards_toward_limit() -> None:
    deck = [_card(f"c{i}") for i in range(5)]
    state = _build_state(deck)
    player = state.players["p1"]
    player.hand = [f"h{i}" for i in range(8)]
    player.face_down_queue.clear()
    player.face_down_queue.extend(["queued_1", "queued_2"])
    events = draw_phase(state, "p1")
    assert len(player.hand) == 8
    assert len(state.draw_pile) == 5
    assert events == []


def test_draw_phase_counts_deterrents_toward_limit() -> None:
    deck = [_card(f"c{i}") for i in range(5)]
    state = _build_state(deck)
    player = state.players["p1"]
    player.hand = [f"h{i}" for i in range(8)]
    player.deterrents = ["deterrent_1", "deterrent_2"]
    events = draw_phase(state, "p1")
    assert len(player.hand) == 8
    assert len(state.draw_pile) == 5
    assert events == []


def test_draw_phase_moves_secrets_to_queue() -> None:
    deck = [_card("secret_card", CardCategory.SECRET), _card("regular")]
    state = _build_state(deck)
    player = state.players["p1"]
    player.hand = []
    events = draw_phase(state, "p1")
    assert "secret_card" in player.secrets
    assert "secret_card" not in player.hand
    assert any(event.event_type == "secret_queued" for event in events)


def test_set_face_down_cards_updates_queue() -> None:
    player = PlayerState(player_id="p1", population=[10])
    player.hand = ["a", "b", "c"]
    set_face_down_cards(player, ["a", "b"])
    queue = list(player.face_down_queue)
    assert queue == ["a", "b"]
    assert player.hand == ["c"]


def test_advance_queue_reveals_face_up() -> None:
    cards = [
        Card("x", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("y", CardCategory.WARHEAD, "Warhead", value=5),
    ]
    state = _build_state(cards)
    player = state.players["p1"]
    player.hand = ["x", "y"]
    set_face_down_cards(player, ["x", "y"])
    event = advance_queue(state, player)
    assert event is not None
    assert event.event_type == "delivery_ready"
    assert list(player.face_down_queue)[0] == "y"


def test_set_face_down_truncates_extra_entries() -> None:
    player = PlayerState(player_id="p1", population=[10])
    player.hand = ["a", "b", "c"]
    entries = [f"card_{i}" for i in range(FACE_DOWN_SLOTS + 1)]
    player.hand.extend(entries)
    set_face_down_cards(player, entries)
    queue = list(player.face_down_queue)
    assert queue == entries[:FACE_DOWN_SLOTS]
