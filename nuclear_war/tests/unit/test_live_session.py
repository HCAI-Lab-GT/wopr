from __future__ import annotations

import pytest

from nuclear_war_env.live_session import (
    LiveSession,
    LiveSessionConfig,
    LiveSessionError,
)
from nuclear_war_env.replay_validation import validate_replay_payload


def test_live_session_starts_with_pending_decision() -> None:
    session = _start_session()

    assert session.session_payload()["seed"] == 42
    assert session.session_payload()["state_version"] == 1
    assert session.decision_payload()["pending"] is True
    assert session.state_payload()["players"][0]["player_id"] == "player_0"


def test_apply_decision_by_action_id_advances_version_and_logs_action() -> None:
    session = _start_session()
    decision = session.decision_payload()
    action_id = decision["legal_actions"][0]["action_id"]
    state_version = decision["state_version"]

    result = session.apply_action_id(action_id, state_version=state_version)

    assert result["ok"] is True
    assert result["state_version"] == state_version + 1
    assert result["decision"]["state_version"] == state_version + 1
    assert session.artifacts_payload()["replay"]["actions"]


def test_artifact_replay_validates_after_session_start() -> None:
    session = _start_session()

    validate_replay_payload(session.artifacts_payload()["replay"], in_progress=True)


def test_artifact_replay_validates_after_legal_decision() -> None:
    session = _start_session()
    decision = session.decision_payload()
    action_id = decision["legal_actions"][0]["action_id"]

    session.apply_action_id(action_id, state_version=decision["state_version"])

    validate_replay_payload(session.artifacts_payload()["replay"], in_progress=True)


def test_stale_state_submission_fails_closed() -> None:
    session = _start_session()
    action_id = session.decision_payload()["legal_actions"][0]["action_id"]
    session.apply_action_id(action_id, state_version=session.state_version)

    with pytest.raises(LiveSessionError) as error:
        session.apply_action_id(action_id, state_version=1)

    assert error.value.code == "stale_state"


def test_invalid_action_id_does_not_mutate_state() -> None:
    session = _start_session()
    state_version = session.state_version
    actions_before = list(session.artifacts_payload()["replay"]["actions"])

    with pytest.raises(LiveSessionError) as error:
        session.apply_action_id("unknown-action-id", state_version=state_version)

    assert error.value.code == "unknown_action"
    assert session.state_version == state_version
    assert session.artifacts_payload()["replay"]["actions"] == actions_before


def test_manual_action_rejects_agent_seat_decision() -> None:
    session = _start_session(controlled_players=())
    decision = session.decision_payload()
    action_id = decision["legal_actions"][0]["action_id"]
    state_version = session.state_version
    actions_before = list(session.artifacts_payload()["replay"]["actions"])

    with pytest.raises(LiveSessionError) as error:
        session.apply_action_id(action_id, state_version=state_version)

    assert error.value.code == "agent_player"
    assert session.state_version == state_version
    assert session.artifacts_payload()["replay"]["actions"] == actions_before


def test_step_agent_advances_version_with_heuristic_choice() -> None:
    session = _start_session(controlled_players=())
    state_version = session.state_version

    result = session.step_agent(state_version=state_version)

    assert result["ok"] is True
    assert result["state_version"] == state_version + 1
    assert session.artifacts_payload()["replay"]["actions"]


def test_agent_only_session_records_terminal_completion() -> None:
    session = _start_session(seed=1, max_turns=500, controlled_players=())

    for _ in range(500):
        decision = session.decision_payload()
        if not decision["pending"]:
            break
        session.step_agent(state_version=decision["state_version"])
    else:
        raise AssertionError("live session did not reach completion within 500 steps")

    replay = session.artifacts_payload()["replay"]

    assert session.session_payload()["status"] == "complete"
    assert replay["termination_reason"] in {
        "no_players_remaining",
        "one_player_remaining",
    }
    validate_replay_payload(replay)


def _start_session(
    *,
    seed: int = 42,
    max_turns: int = 20,
    controlled_players: tuple[str, ...] = ("player_0",),
) -> LiveSession:
    config = LiveSessionConfig(
        players=3,
        seed=seed,
        max_turns=max_turns,
        controlled_players=controlled_players,
    )
    return LiveSession.start(config)
