"""Press artifact sidecar tests."""

from __future__ import annotations

import pytest

from nuclear_war_concordia.press_artifacts import (
    build_press_artifact,
    validate_press_artifact,
)
from nuclear_war_env.agent_protocol import DecisionAgent
from nuclear_war_env.simulation import (
    SimulationConfig,
    run_table_simulation_with_decision_agents,
)


class _FirstLegalAgent(DecisionAgent):
    def choose(self, observation, options):
        return options[0]


def _replay() -> dict:
    config = SimulationConfig(
        mode="table",
        players=4,
        seed=81,
        agent="decision_heuristic",
        max_turns=2,
        press=False,
    )
    agents = {
        pid: _FirstLegalAgent()
        for pid in ["player_0", "player_1", "player_2", "player_3"]
    }
    return run_table_simulation_with_decision_agents(config, agents)


def _message(turn: int, speaker: str) -> dict:
    return {
        "message_id": f"press:{turn}:{speaker}:1",
        "turn": turn,
        "round": turn,
        "speaker": speaker,
        "audience": "public",
        "visibility": "public",
        "pass": 1,
        "decision_type": "press",
        "rendered_observation": {},
        "prior_messages": [],
        "prompt": "",
        "prompts": [],
        "legal_options": [],
        "raw_response": "",
        "raw_responses": [],
        "parse_result": {"message": None, "rationale": None, "declined": True},
        "text": None,
        "retries": 0,
        "validation_errors": [],
        "stated_rationale": None,
        "provider_latency_ms": None,
        "provider_cost": None,
        "provider_usage": None,
        "provider_label": None,
        "provider_model": None,
        "linked_decision_traces": [],
    }


def test_build_press_artifact_wraps_messages_with_replay_reference() -> None:
    replay = _replay()
    messages = [_message(turn=2, speaker="player_0")]

    artifact = build_press_artifact(replay, messages, "press_light")

    assert artifact["schema_version"] == 1
    assert artifact["press_mode"] == "press_light"
    assert artifact["replay"] == {
        "mode": "table",
        "seed": 81,
        "agent": "decision_heuristic",
        "players": 4,
        "turns": 2,
    }
    assert artifact["messages"] is messages


@pytest.mark.parametrize(
    "payload",
    [
        {
            "schema_version": 1,
            "press_mode": "press_light",
            "replay": {},
            "messages": [],
        },
        {
            "schema_version": 1,
            "press_mode": "multi_turn_public",
            "replay": {"mode": "table", "seed": 81},
            "messages": [],
        },
        {"schema_version": 1, "press_mode": "press_light", "replay": None},
    ],
)
def test_validate_press_artifact_rejects_invalid(payload: dict) -> None:
    with pytest.raises(ValueError):
        validate_press_artifact(payload, _replay())


def test_validate_press_artifact_accepts_valid() -> None:
    replay = _replay()
    artifact = build_press_artifact(replay, [], "press_light")
    validate_press_artifact(artifact, replay)


def test_validate_press_artifact_rejects_selected_action_id() -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    message["selected_action_id"] = "player_0:draw"
    with pytest.raises(ValueError, match="selected_action_id"):
        artifact = {
            "schema_version": 1,
            "press_mode": "press_light",
            "replay": artifact_replay(replay),
            "messages": [message],
        }
        validate_press_artifact(artifact, replay)


def artifact_replay(replay: dict) -> dict:
    return {
        "mode": replay["mode"],
        "seed": replay["seed"],
        "agent": replay["agent"],
        "players": replay["players"],
        "turns": replay["turns"],
    }


def test_build_press_artifact_accepts_full_press_mode() -> None:
    replay = _replay()
    artifact = build_press_artifact(replay, [], "full_press")

    assert artifact["press_mode"] == "full_press"
    validate_press_artifact(artifact, replay)


def test_validate_press_artifact_accepts_private_message_with_recipient() -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    message["visibility"] = "private"
    message["audience"] = "player_1"
    message["recipient"] = "player_1"
    artifact = {
        "schema_version": 1,
        "press_mode": "full_press",
        "replay": artifact_replay(replay),
        "messages": [message],
    }
    validate_press_artifact(artifact, replay)


def test_validate_press_artifact_rejects_private_without_recipient() -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    message["visibility"] = "private"
    message["audience"] = "player_1"
    artifact = {
        "schema_version": 1,
        "press_mode": "full_press",
        "replay": artifact_replay(replay),
        "messages": [message],
    }
    with pytest.raises(ValueError, match="recipient"):
        validate_press_artifact(artifact, replay)


def test_validate_press_artifact_rejects_public_with_recipient() -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    message["recipient"] = "player_1"
    artifact = {
        "schema_version": 1,
        "press_mode": "press_light",
        "replay": artifact_replay(replay),
        "messages": [message],
    }
    with pytest.raises(ValueError, match="recipient"):
        validate_press_artifact(artifact, replay)


def test_validate_press_artifact_validates_commitment_shape() -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    message["commitment"] = {"kind": "stand_down", "target_round": 3}
    artifact = {
        "schema_version": 1,
        "press_mode": "full_press",
        "replay": artifact_replay(replay),
        "messages": [message],
    }
    validate_press_artifact(artifact, replay)


@pytest.mark.parametrize(
    "commitment",
    [
        {"target_round": 3},
        {"kind": ""},
        {"kind": "x", "target_round": 0},
        {"kind": "x", "target_round": "3"},
        {"kind": "x", "extra": 1},
        "not a dict",
    ],
)
def test_validate_press_artifact_rejects_invalid_commitment(commitment) -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    message["commitment"] = commitment
    artifact = {
        "schema_version": 1,
        "press_mode": "full_press",
        "replay": artifact_replay(replay),
        "messages": [message],
    }
    with pytest.raises(ValueError, match="commitment"):
        validate_press_artifact(artifact, replay)


def _single_message_artifact(replay: dict, message: dict, press_mode: str) -> dict:
    return {
        "schema_version": 1,
        "press_mode": press_mode,
        "replay": artifact_replay(replay),
        "messages": [message],
    }


@pytest.mark.parametrize("bad_pass", [-3, 0, True, "1", 1.0])
def test_validate_press_artifact_rejects_non_positive_pass(bad_pass) -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    message["pass"] = bad_pass
    with pytest.raises(ValueError, match="pass"):
        validate_press_artifact(
            _single_message_artifact(replay, message, "press_light"), replay
        )


def test_validate_press_artifact_rejects_missing_prompts() -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    del message["prompts"]
    with pytest.raises(ValueError, match="prompts"):
        validate_press_artifact(
            _single_message_artifact(replay, message, "press_light"), replay
        )


@pytest.mark.parametrize("field", ["prompts", "raw_responses", "prior_messages"])
def test_validate_press_artifact_rejects_non_list_trace_fields(field) -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    message[field] = "not a list"
    with pytest.raises(ValueError, match=field):
        validate_press_artifact(
            _single_message_artifact(replay, message, "press_light"), replay
        )


@pytest.mark.parametrize("bad_retries", [-1, True, "0", 1.0])
def test_validate_press_artifact_rejects_invalid_retries(bad_retries) -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    message["retries"] = bad_retries
    with pytest.raises(ValueError, match="retries"):
        validate_press_artifact(
            _single_message_artifact(replay, message, "press_light"), replay
        )


@pytest.mark.parametrize("public_only_mode", ["press_light", "multi_turn_public"])
def test_validate_press_artifact_rejects_private_in_public_only_mode(
    public_only_mode,
) -> None:
    replay = _replay()
    message = _message(turn=2, speaker="player_0")
    message["visibility"] = "private"
    message["audience"] = "player_1"
    message["recipient"] = "player_1"
    with pytest.raises(ValueError, match="private"):
        validate_press_artifact(
            _single_message_artifact(replay, message, public_only_mode), replay
        )
