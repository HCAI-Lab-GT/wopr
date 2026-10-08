"""Card effect tests against registry-backed metadata."""

from __future__ import annotations

from nuclear_war_env.actions import ActionType, apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.cards_registry import (
    CardType,
    card_from_record,
    load_card_registry,
)
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.engine.draw import draw_phase
from nuclear_war_env.rules import RULES_PATH
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state(cards: list[Card]) -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards(cards)
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    return state


def _first_card(card_type: CardType, name: str | None = None) -> Card:
    registry = load_card_registry(RULES_PATH)
    for record in registry.values():
        if record.type is card_type and (name is None or record.name == name):
            return card_from_record(record)
    raise AssertionError(f"Missing registry card: {card_type}")


def test_postal_propaganda_uses_registry_value() -> None:
    card = _first_card(CardType.PROPAGANDA, "Propaganda 5M")
    state = _state([card])
    state.peace = True
    state.players["p1"].pending_orders["propaganda"] = [card.identifier]
    state.players["p1"].pending_orders["propaganda_orders"] = {card.identifier: "p2"}
    events = execute_postal_turn(state)
    assert sum(state.players["p1"].population) == 35
    assert sum(state.players["p2"].population) == 25
    assert any(event.event_type == "propaganda_effect" for event in events)


def test_postal_intercept_uses_registry_labels() -> None:
    delivery = _first_card(CardType.CARRIER, "Polaris Missile")
    warhead = _first_card(CardType.WARHEAD, "Warhead 10 Mt")
    defense = _first_card(CardType.ANTI_MISSILE, "Anti-Missile (P)")
    state = _state([delivery, warhead, defense])
    state.players["p1"].pending_orders["launches"] = {
        delivery.identifier: {
            "delivery": delivery.identifier,
            "capacity": 1,
            "warheads": [warhead.identifier],
            "target": "p2",
        }
    }
    state.players["p2"].pending_orders["defense"] = [defense.identifier]
    events = execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 30
    assert any(event.event_type == "intercept_success" for event in events)


def test_secret_population_effect_applies_to_target() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"steal_population_millions": 2},
    )
    state = _state([secret])
    state.players["p1"].secrets = [secret.identifier]
    state.players["p1"].pending_orders["secret_targets"] = {secret.identifier: "p2"}
    events = execute_postal_turn(state)
    assert sum(state.players["p1"].population) == 32
    assert sum(state.players["p2"].population) == 28
    assert any(event.event_type == "secret_population_stolen" for event in events)


def test_secret_skip_turn_effect_limits_next_action() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"target_loses_turns": 1},
    )
    state = _state([secret])
    state.players["p1"].secrets = [secret.identifier]
    state.players["p1"].pending_orders["secret_targets"] = {secret.identifier: "p2"}
    execute_postal_turn(state)
    actions = legal_actions(state, "p2", "postal")
    assert [action.action_type for action in actions] == [ActionType.PASS]
    events = apply_action(state, actions[0])
    assert state.players["p2"].pending_orders.get("skip_turns") is None
    assert any(event.event_type == "turn_skipped" for event in events)


def test_draw_phase_queues_top_secret_like_secret() -> None:
    top_secret = _first_card(CardType.TOP_SECRET, "Disastrous Earthquake")
    state = _state([top_secret])
    state.draw_pile = [top_secret]
    state.players["p1"].hand = []
    events = draw_phase(state, "p1")
    assert state.players["p1"].secrets == [top_secret.identifier]
    assert top_secret.identifier not in state.players["p1"].hand
    assert any(event.event_type == "secret_queued" for event in events)


def test_stolen_secret_waits_until_following_postal_turn() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"steal_population_millions": 2},
    )
    state = _state([secret])
    state.players["p2"].secrets = [secret.identifier]
    state.players["p1"].pending_orders["steal_secret"] = "p2"
    state.players["p1"].pending_orders["secret_targets"] = {secret.identifier: "p2"}
    events = execute_postal_turn(state)
    assert sum(state.players["p1"].population) == 30
    assert sum(state.players["p2"].population) == 30
    assert state.players["p1"].secrets == [secret.identifier]
    assert not any(event.event_type == "secret_population_stolen" for event in events)
