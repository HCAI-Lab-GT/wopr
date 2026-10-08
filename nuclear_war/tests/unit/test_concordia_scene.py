"""Concordia scene rendering tests."""

from __future__ import annotations

from nuclear_war_concordia.scene import render_concordia_scene
from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.observation import (
    DecisionObservation,
    Observation,
    PrivatePlayerObservation,
    PublicPlayerObservation,
)


def test_render_concordia_scene_includes_identity_observation_and_options() -> None:
    options = [
        build_action("player_0", ActionType.DRAW, "Draw"),
        build_action("player_0", ActionType.PASS, "Pass"),
    ]
    scene = render_concordia_scene(
        observation=_observation(options),
        options=options,
        identity={
            "name": "Analyst Zero",
            "role": "cautious nuclear commander",
            "objective": "survive while preserving leverage",
        },
        validation_feedback=[],
    )

    assert scene.payload["player_id"] == "player_0"
    assert scene.payload["identity"]["name"] == "Analyst Zero"
    assert scene.payload["decision_type"] == "pass"
    assert scene.payload["legal_options"][0]["action_id"] == options[0].action_id
    assert "What kind of situation is this?" in scene.text
    assert options[1].action_id in scene.text


def test_render_concordia_scene_declares_no_press_when_press_memory_absent() -> None:
    options = [build_action("player_0", ActionType.PASS, "Pass")]
    scene = render_concordia_scene(
        observation=_observation(options),
        options=options,
        identity={"name": "Analyst Zero"},
        validation_feedback=[],
    )

    assert "No press or player communication is available in this run." in scene.text


def test_render_concordia_scene_points_at_transcript_with_press_memory() -> None:
    options = [build_action("player_0", ActionType.PASS, "Pass")]
    press_memory = [
        {"turn": 1, "speaker": "player_1", "text": "Stand down.", "audience": "public"}
    ]
    scene = render_concordia_scene(
        observation=_observation(options),
        options=options,
        identity={"name": "Analyst Zero"},
        validation_feedback=[],
        press_memory=press_memory,
    )

    assert "No press or player communication is available" not in scene.text
    assert "press_memory" in scene.text
    assert scene.payload["press_memory"] == press_memory


def _observation(options) -> Observation:
    return Observation(
        player_id="player_0",
        ruleset="table",
        turn=1,
        peace=True,
        self=PrivatePlayerObservation(
            population=20,
            hand=["card-a"],
            secrets=[],
            deterrents=[None, None],
            face_up=None,
            face_down_queue=[None, None],
            final_strike_cards=[],
            pending_orders={},
            alive=True,
            at_war=False,
        ),
        players={"player_1": _public_player(30)},
        draw_count=10,
        discard_count=0,
        decision=DecisionObservation(
            agent_id="player_0",
            decision_type=DecisionType.PASS,
            options=options,
        ),
    )


def _public_player(population: int) -> PublicPlayerObservation:
    return PublicPlayerObservation(
        population=population,
        hand_count=3,
        secret_count=0,
        deterrent_count=0,
        face_up=None,
        face_down_count=2,
        alive=True,
        at_war=False,
    )
