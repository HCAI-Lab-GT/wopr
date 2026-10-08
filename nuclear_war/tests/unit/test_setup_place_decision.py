"""Opening face-down commitment surfaced as a SETUP_PLACE agent decision."""

from __future__ import annotations

import pytest

from nuclear_war_env.action_models import ActionType
from nuclear_war_env.decision_loop import (
    apply_decision,
    pending_decision,
    start_game,
)
from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.replay_action_validation import validate_action_shapes
from nuclear_war_env.setup_game import create_game_state
from nuclear_war_env.state import FACE_DOWN_SLOTS


def _deferred_state(seed: int = 5, players: int = 3):
    return create_game_state("table", players, seed=seed, defer_opening_commitment=True)


def test_deferred_setup_leaves_face_down_queue_empty() -> None:
    state = _deferred_state()
    for player in state.players.values():
        assert list(player.face_down_queue) == [None] * FACE_DOWN_SLOTS
        assert len(player.hand) >= 2


def test_default_setup_still_auto_commits() -> None:
    state = create_game_state("table", 3, seed=5)
    for player in state.players.values():
        assert sum(1 for c in player.face_down_queue if c is not None) == 2
    start_game(state)
    decision = pending_decision(state)
    assert decision is not None
    assert decision.decision_type is not DecisionType.SETUP_PLACE


def test_setup_place_decisions_offered_per_player_in_hand_order() -> None:
    state = _deferred_state()
    start_game(state)
    for player_id in state.players:
        expected_first_two = list(state.players[player_id].hand[:2])
        for _slot in range(2):
            decision = pending_decision(state)
            assert decision is not None
            assert decision.decision_type is DecisionType.SETUP_PLACE
            assert decision.agent_id == player_id
            hand = state.players[player_id].hand
            assert [opt.payload["cards"][0] for opt in decision.options] == list(hand)
            assert all(
                opt.action_type is ActionType.SETUP_PLACE for opt in decision.options
            )
            apply_decision(state, decision.options[0])
        committed = [c for c in state.players[player_id].face_down_queue if c]
        assert committed == expected_first_two
    decision = pending_decision(state)
    assert decision is not None
    assert decision.decision_type is not DecisionType.SETUP_PLACE


def test_options_first_reproduces_legacy_auto_commit() -> None:
    legacy = create_game_state("table", 3, seed=9)
    deferred = _deferred_state(seed=9)
    start_game(deferred)
    while (decision := pending_decision(deferred)) is not None and (
        decision.decision_type is DecisionType.SETUP_PLACE
    ):
        apply_decision(deferred, decision.options[0])
    for player_id in legacy.players:
        assert list(legacy.players[player_id].face_down_queue) == list(
            deferred.players[player_id].face_down_queue
        )
        assert legacy.players[player_id].hand == deferred.players[player_id].hand


def test_setup_place_replay_payload_validates() -> None:
    action = {
        "player_id": "player_0",
        "action_id": 'player_0:setup_place:{"cards":["warhead_10mt#1"]}',
        "action_type": "setup_place",
        "payload": {"cards": ["warhead_10mt#1"]},
    }
    validate_action_shapes(action, 0, "table")


def test_setup_place_rejected_in_postal_replay() -> None:
    # setup_place is table-only: postal setup auto-commits and no postal engine
    # path produces it, so a postal replay carrying it is corrupt.
    action = {
        "player_id": "player_0",
        "action_id": 'player_0:setup_place:{"cards":["warhead_10mt#1"]}',
        "action_type": "setup_place",
        "payload": {"cards": ["warhead_10mt#1"]},
    }
    with pytest.raises(ValueError, match="requires table mode"):
        validate_action_shapes(action, 0, "postal")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"cards": []},
        {"cards": ["a#1", "b#2"]},
        {"cards": "a#1"},
        {"card": "a#1"},
    ],
)
def test_setup_place_replay_payload_rejects_bad_shapes(payload: dict) -> None:
    action = {
        "player_id": "player_0",
        "action_id": "player_0:setup_place",
        "action_type": "setup_place",
        "payload": payload,
    }
    with pytest.raises(ValueError):
        validate_action_shapes(action, 0, "table")
