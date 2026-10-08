"""Peace-restoration strategy replacement (STRATEGY_REPLACE decision window)."""

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
from nuclear_war_env.simulation import SimulationConfig, run_simulation


def _state_at_first_turn_decision():
    """A started game advanced past setup to the first normal decision."""
    state = create_game_state("table", 3, seed=5, defer_opening_commitment=True)
    start_game(state)
    while (decision := pending_decision(state)) is not None and (
        decision.decision_type is DecisionType.SETUP_PLACE
    ):
        apply_decision(state, decision.options[0])
    return state


def _force_peace_transition(state) -> None:
    """Drive the cursor through war -> peace so the loop sees a restoration."""
    state.peace = False
    decision = pending_decision(state)
    assert decision is not None
    apply_decision(state, decision.options[0])  # loop observes the war state
    state.peace = True
    decision = pending_decision(state)
    assert decision is not None
    apply_decision(state, decision.options[0])  # loop observes the restoration


def test_peace_restoration_opens_strategy_replace_window() -> None:
    state = _state_at_first_turn_decision()
    _force_peace_transition(state)
    decision = pending_decision(state)
    assert decision is not None
    assert decision.decision_type is DecisionType.STRATEGY_REPLACE
    # Decline is options[0] (engine-orders pattern: pick-first keeps old behavior).
    assert decision.options[0].payload == {}
    player = state.players[decision.agent_id]
    slots = [i for i, c in enumerate(player.face_down_queue) if c is not None]
    replacements = decision.options[1:]
    assert replacements
    assert {opt.payload["slot"] for opt in replacements} == set(slots)
    assert all(opt.payload["card"] in player.hand for opt in replacements)
    assert all(
        opt.action_type is ActionType.STRATEGY_REPLACE for opt in decision.options
    )


def test_decline_ends_the_player_window() -> None:
    state = _state_at_first_turn_decision()
    _force_peace_transition(state)
    decision = pending_decision(state)
    assert decision is not None
    first_player = decision.agent_id
    apply_decision(state, decision.options[0])  # decline
    decision = pending_decision(state)
    assert decision is not None
    if decision.decision_type is DecisionType.STRATEGY_REPLACE:
        assert decision.agent_id != first_player


def test_replace_swaps_hand_card_into_slot_and_returns_old_card() -> None:
    state = _state_at_first_turn_decision()
    _force_peace_transition(state)
    decision = pending_decision(state)
    assert decision is not None
    player = state.players[decision.agent_id]
    replace = decision.options[1]
    slot = replace.payload["slot"]
    new_card = replace.payload["card"]
    old_card = player.face_down_queue[slot]
    apply_decision(state, replace)
    assert player.face_down_queue[slot] == new_card
    assert old_card in player.hand
    assert new_card not in player.hand


def test_window_allows_at_most_two_replacements() -> None:
    state = _state_at_first_turn_decision()
    _force_peace_transition(state)
    decision = pending_decision(state)
    assert decision is not None
    first_player = decision.agent_id
    for _ in range(2):
        assert decision is not None
        assert decision.decision_type is DecisionType.STRATEGY_REPLACE
        assert decision.agent_id == first_player
        apply_decision(state, decision.options[1])
        decision = pending_decision(state)
    if decision is not None and (
        decision.decision_type is DecisionType.STRATEGY_REPLACE
    ):
        assert decision.agent_id != first_player


def test_heuristic_full_game_records_declines_and_outcome_is_pinned() -> None:
    # Seed 8: after the #84 final-retaliation merge, seed 1 ends in mutual
    # annihilation before peace is ever restored, so it no longer opens a
    # window. Seed 8 restores peace and reaches a single survivor, exercising
    # the decline path and a pinned outcome.
    result = run_simulation(SimulationConfig("table", 3, 8, "heuristic", max_turns=80))
    replaces = [
        action
        for action in result["actions"]
        if action["action_type"] == "strategy_replace"
    ]
    assert replaces, "expected a peace restoration to open the window in seed 8"
    assert all(action["payload"] == {} for action in replaces)
    # Heuristic golden outcome for ("heuristic", 8) is unchanged by decline-only
    # windows (options[0] declines, consuming no RNG).
    assert result["winner"] == "player_0"
    assert result["termination_reason"] == "one_player_remaining"


def test_strategy_replace_replay_payload_validates() -> None:
    for payload in ({}, {"card": "warhead_10mt#1", "slot": 1}):
        action = {
            "player_id": "player_0",
            "action_type": "strategy_replace",
            "payload": payload,
        }
        action["action_id"] = "player_0:strategy_replace" + (
            ':{"card":"warhead_10mt#1","slot":1}' if payload else ""
        )
        validate_action_shapes(action, 0, "table")


def test_strategy_replace_rejected_in_postal_replay() -> None:
    # strategy_replace is table-only: the peace-restoration window only opens in
    # the table decision loop, so a postal replay carrying it is corrupt.
    action = {
        "player_id": "player_0",
        "action_id": "player_0:strategy_replace",
        "action_type": "strategy_replace",
        "payload": {},
    }
    with pytest.raises(ValueError, match="requires table mode"):
        validate_action_shapes(action, 0, "postal")


@pytest.mark.parametrize(
    "payload",
    [
        {"card": "a#1"},
        {"slot": 0},
        {"card": "a#1", "slot": 2},
        {"card": "a#1", "slot": -1},
        {"card": 3, "slot": 0},
        {"card": "a#1", "slot": 0, "extra": 1},
    ],
)
def test_strategy_replace_replay_payload_rejects_bad_shapes(payload: dict) -> None:
    action = {
        "player_id": "player_0",
        "action_id": "player_0:strategy_replace",
        "action_type": "strategy_replace",
        "payload": payload,
    }
    with pytest.raises(ValueError):
        validate_action_shapes(action, 0, "table")
