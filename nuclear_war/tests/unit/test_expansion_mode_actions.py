"""Expansion mode legal-action boundary tests."""

from __future__ import annotations

from nuclear_war_env.actions import legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.expansions import EXPANSION_MECHANICS
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_table_mode_never_exposes_postal_expansion_actions() -> None:
    actions = legal_actions(_state_with_expansion_cards(), "p1", mode="table")

    assert not [
        action for action in actions if action.action_type.value.startswith("postal_")
    ]


def _state_with_expansion_cards() -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    cards = [
        Card(
            mechanic.registry_id,
            CardCategory.SPECIAL,
            mechanic.postal_effect,
            metadata={"postal_effect": mechanic.postal_effect},
        )
        for mechanic in EXPANSION_MECHANICS
    ]
    state.register_cards(cards)
    state.players["p1"].hand = [card.identifier for card in cards]
    return state
