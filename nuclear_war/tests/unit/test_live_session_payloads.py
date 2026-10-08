from __future__ import annotations

import json

from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.engine.decision import Decision, DecisionType
from nuclear_war_env.live_session_payloads import (
    decision_payload,
    legal_action_payload,
    player_payload,
    state_payload,
)
from nuclear_war_env.setup_game import create_game_state


def test_legal_action_payload_is_json_safe() -> None:
    action = build_action(
        "player_0",
        ActionType.ENQUEUE,
        "Place card",
        {"cards": ["nw_base_1"]},
    )

    payload = legal_action_payload(action)

    assert payload["action_id"] == action.action_id
    assert payload["player_id"] == "player_0"
    assert payload["action_type"] == "enqueue"
    assert payload["label"] == "Place card"
    assert payload["payload"] == {"cards": ["nw_base_1"]}
    json.dumps(payload, allow_nan=False)


def test_decision_payload_includes_version_and_options() -> None:
    action = build_action(
        "player_0",
        ActionType.ENQUEUE,
        "Place card",
        {"cards": ["nw_base_1"]},
    )
    decision = Decision(
        "player_0",
        DecisionType.PLACE,
        [action],
        context={"phase": "place"},
    )

    payload = decision_payload(decision, state_version=3)

    assert payload["pending"] is True
    assert payload["state_version"] == 3
    assert payload["agent_id"] == "player_0"
    assert payload["decision_type"] == "place"
    assert payload["context"] == {"phase": "place"}
    assert payload["legal_actions"][0]["action_id"] == action.action_id
    json.dumps(payload, allow_nan=False)


def test_decision_payload_reports_absent_decision() -> None:
    assert decision_payload(None, state_version=5) == {
        "pending": False,
        "state_version": 5,
    }


def test_player_payload_reports_public_counts_and_queue() -> None:
    state = create_game_state("table", player_count=3, seed=42)

    payload = player_payload(state, "player_0")

    assert payload["player_id"] == "player_0"
    assert payload["population"] == sum(state.players["player_0"].population)
    assert payload["alive"] is True
    assert payload["hand_count"] == len(state.players["player_0"].hand)
    assert payload["secret_count"] == len(state.players["player_0"].secrets)
    assert payload["queue"] == list(state.players["player_0"].face_down_queue)
    json.dumps(payload, allow_nan=False)


def test_state_payload_includes_players_events_and_warnings() -> None:
    state = create_game_state("table", player_count=3, seed=42)
    recent_events = [{"turn": 1, "event_type": "draw"}]

    payload = state_payload(
        state,
        state_version=2,
        source_label="live local session",
        recent_events=recent_events,
    )

    assert payload["state_version"] == 2
    assert payload["turn"] == state.turn
    assert payload["source_label"] == "live local session"
    assert len(payload["players"]) == 3
    assert payload["recent_events"] == recent_events
    assert payload["warnings"] == []
    json.dumps(payload, allow_nan=False)
