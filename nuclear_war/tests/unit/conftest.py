from __future__ import annotations

import pytest

from nuclear_war_env.action_models import ActionType, LegalAction, build_action
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.observation import (
    DecisionObservation,
    Observation,
    PrivatePlayerObservation,
    PublicPlayerObservation,
)
from nuclear_war_env.state import GameState, Ruleset, create_players


@pytest.fixture
def faction_options() -> list[LegalAction]:
    return [
        build_action("p1", ActionType.PASS, "Pass"),
        build_action("p1", ActionType.TARGET, "Target p3", {"target": "p3"}),
    ]


@pytest.fixture
def faction_observation(faction_options: list[LegalAction]) -> Observation:
    return Observation(
        player_id="p1",
        ruleset="table",
        turn=1,
        peace=False,
        self=PrivatePlayerObservation(
            population=20,
            hand=["missile_1"],
            secrets=[],
            deterrents=[None, None],
            face_up=None,
            face_down_queue=[None, None],
            final_strike_cards=[],
            pending_orders={},
            alive=True,
            at_war=False,
        ),
        players={
            "p2": PublicPlayerObservation(10, 2, 1, 0, None, 0, True, False),
            "p3": PublicPlayerObservation(30, 2, 1, 0, None, 0, True, False),
        },
        draw_count=12,
        discard_count=0,
        decision=DecisionObservation(
            agent_id="p1",
            decision_type=DecisionType.LAUNCH_TARGET,
            options=faction_options,
        ),
    )


@pytest.fixture
def retaliation_state() -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["player_0", "player_1", "player_2"], 30),
        draw_pile=[],
    )
    state.register_cards(
        [
            Card(
                "attack_delivery",
                CardCategory.DELIVERY,
                "Attack Missile",
                metadata={"capacity": 1, "max_yield_megatons": 20},
            ),
            Card("attack_warhead", CardCategory.WARHEAD, "Attack Warhead 50", value=50),
            Card(
                "retaliation_delivery",
                CardCategory.DELIVERY,
                "Retaliation Missile",
                metadata={"capacity": 1},
            ),
            Card(
                "retaliation_warhead",
                CardCategory.WARHEAD,
                "Retaliation Warhead 10",
                value=10,
            ),
        ]
    )
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    return state
