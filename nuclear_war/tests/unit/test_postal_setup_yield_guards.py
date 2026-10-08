"""Postal setup legal-action yield guard tests."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_env.actions import ActionType, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.state import GameState, Ruleset, create_players


@pytest.mark.parametrize(
    ("postal_effect", "action_type", "pending_orders"),
    [
        ("cruise_missile", ActionType.POSTAL_CRUISE_LAUNCH, {}),
        ("submarine", ActionType.POSTAL_SUBMARINE_LAUNCH, {}),
        (
            "space_platform",
            ActionType.POSTAL_SPACE_PLATFORM_LAUNCH,
            {},
        ),
        ("space_shuttle", ActionType.POSTAL_SPACE_SHUTTLE_ATTACK, {}),
        (
            "space_shuttle",
            ActionType.POSTAL_SPACE_SHUTTLE_RELOAD,
            {"space_platforms": {"platform": {"warheads": [10]}}},
        ),
    ],
)
def test_postal_setup_actions_reject_float_warhead_values(
    postal_effect: str,
    action_type: ActionType,
    pending_orders: dict[str, object],
) -> None:
    malformed_value: Any = 10.0
    special = Card(
        "special",
        CardCategory.SPECIAL,
        "Special",
        metadata={"postal_effect": postal_effect},
    )
    warhead = Card("warhead", CardCategory.WARHEAD, "Warhead", value=malformed_value)
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([special, warhead])
    state.players["p1"].hand = ["special", "warhead"]
    state.players["p1"].pending_orders.update(pending_orders)

    actions = legal_actions(state, "p1", mode="postal")

    assert all(action.action_type is not action_type for action in actions)
