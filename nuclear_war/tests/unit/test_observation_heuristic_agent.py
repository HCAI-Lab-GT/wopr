"""Observation-driven heuristic agent tests."""

from __future__ import annotations

from nuclear_war_agents import ObservationHeuristicAgent
from nuclear_war_env.action_models import ActionType, LegalAction, build_action
from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.observation import (
    DecisionObservation,
    Observation,
    PrivatePlayerObservation,
    PublicPlayerObservation,
)


def test_observation_heuristic_targets_highest_population_option() -> None:
    actions = [
        build_action("p1", ActionType.TARGET, "Target p2", _target("p2")),
        build_action("p1", ActionType.TARGET, "Target p3", _target("p3")),
    ]
    observation = _observation(DecisionType.LAUNCH_TARGET, actions)

    selected = ObservationHeuristicAgent().choose(observation, actions)

    assert selected.payload["target"] == "p3"


def test_observation_heuristic_intercepts_with_card_before_declining() -> None:
    actions = [
        build_action("p2", ActionType.INTERCEPT, "Decline intercept"),
        build_action("p2", ActionType.INTERCEPT, "Use anti-missile", {"card": "a1"}),
    ]
    observation = _observation(DecisionType.INTERCEPT, actions, player_id="p2")

    selected = ObservationHeuristicAgent().choose(observation, actions)

    assert selected.payload == {"card": "a1"}


def _target(player_id: str) -> dict[str, str]:
    return {"delivery": "d1", "target": player_id}


def _observation(
    decision_type: DecisionType,
    options: list[LegalAction],
    player_id: str = "p1",
) -> Observation:
    return Observation(
        player_id=player_id,
        ruleset="table",
        turn=1,
        peace=False,
        self=PrivatePlayerObservation(
            population=20,
            hand=[],
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
            "p2": _public_player(population=10),
            "p3": _public_player(population=40),
        },
        draw_count=0,
        discard_count=0,
        decision=DecisionObservation(
            agent_id=player_id,
            decision_type=decision_type,
            options=options,
        ),
    )


def _public_player(population: int) -> PublicPlayerObservation:
    return PublicPlayerObservation(
        population=population,
        hand_count=0,
        secret_count=0,
        deterrent_count=0,
        face_up=None,
        face_down_count=0,
        alive=True,
        at_war=False,
    )
