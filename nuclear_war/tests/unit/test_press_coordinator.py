"""Press coordinator tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_concordia.agent import FirstLegalConcordiaClient
from nuclear_war_concordia.failure import ConcordiaDecisionFailure
from nuclear_war_concordia.press_coordinator import PressCoordinator


def test_press_coordinator_collects_declines_from_first_legal_clients() -> None:
    sink: list[dict] = []
    coordinator = PressCoordinator(
        speakers=["player_0", "player_1", "player_2", "player_3"],
        clients={pid: FirstLegalConcordiaClient() for pid in _four()},
        identities={pid: {"name": pid} for pid in _four()},
        press_sink=sink,
        max_retries=0,
    )

    log = coordinator.run_round_press(
        observations=_four_observations(),
        round_no=2,
    )

    assert len(sink) == 4
    assert all(record["text"] is None for record in sink)
    assert all(record["parse_result"]["declined"] for record in sink)
    assert len(log) == 4
    assert all(entry["is_decline"] for entry in log)


def test_press_coordinator_injects_prior_messages_into_later_speakers() -> None:
    class ScriptedClient:
        def __init__(self, responses: list[str]) -> None:
            self.responses = responses
            self.index = 0

        def complete(self, scene_text: str) -> str:
            response = self.responses[self.index]
            self.index += 1
            return response

    sink: list[dict] = []
    clients = {
        "player_0": ScriptedClient(['{"message": "Hold fire."}']),
        "player_1": FirstLegalConcordiaClient(),
    }
    coordinator = PressCoordinator(
        speakers=["player_0", "player_1"],
        clients=clients,
        identities={pid: {"name": pid} for pid in ["player_0", "player_1"]},
        press_sink=sink,
        max_retries=0,
    )

    coordinator.run_round_press(observations=_two_observations(), round_no=2)

    player_1_record = next(r for r in sink if r["speaker"] == "player_1")
    assert any(msg["text"] == "Hold fire." for msg in player_1_record["prior_messages"])


def test_press_coordinator_fails_hard_on_parse_failure() -> None:
    class BrokenClient:
        def complete(self, scene_text: str) -> str:
            return "not json"

    coordinator = PressCoordinator(
        speakers=["player_0"],
        clients={"player_0": BrokenClient()},
        identities={"player_0": {"name": "player_0"}},
        press_sink=[],
        max_retries=0,
    )

    with pytest.raises(ConcordiaDecisionFailure, match="press message"):
        coordinator.run_round_press(observations=_one_observation(), round_no=2)


def _four() -> list[str]:
    return ["player_0", "player_1", "player_2", "player_3"]


def _four_observations():
    return _observations(_four())


def _two_observations():
    return _observations(["player_0", "player_1"])


def _one_observation():
    return _observations(["player_0"])


def test_press_coordinator_runs_multiple_passes() -> None:
    sink: list[dict] = []
    coordinator = PressCoordinator(
        speakers=["player_0", "player_1"],
        clients={pid: FirstLegalConcordiaClient() for pid in ["player_0", "player_1"]},
        identities={pid: {"name": pid} for pid in ["player_0", "player_1"]},
        press_sink=sink,
        max_retries=0,
        passes=2,
    )

    coordinator.run_round_press(observations=_two_observations(), round_no=2)

    assert len(sink) == 4
    player_0_passes = sorted(r["pass"] for r in sink if r["speaker"] == "player_0")
    player_1_passes = sorted(r["pass"] for r in sink if r["speaker"] == "player_1")
    assert player_0_passes == [1, 2]
    assert player_1_passes == [1, 2]


def test_press_coordinator_pass_two_sees_pass_one_messages() -> None:
    class ScriptedClient:
        def __init__(self, responses: list[str]) -> None:
            self.responses = responses
            self.index = 0

        def complete(self, scene_text: str) -> str:
            response = self.responses[self.index]
            self.index += 1
            return response

    sink: list[dict] = []
    coordinator = PressCoordinator(
        speakers=["player_0", "player_1"],
        clients={
            "player_0": ScriptedClient(
                ['{"message": "Pass one."}', '{"message": "Pass two."}']
            ),
            "player_1": FirstLegalConcordiaClient(),
        },
        identities={pid: {"name": pid} for pid in ["player_0", "player_1"]},
        press_sink=sink,
        max_retries=0,
        passes=2,
    )

    coordinator.run_round_press(observations=_two_observations(), round_no=2)

    player_1_pass_two = next(
        r for r in sink if r["speaker"] == "player_1" and r["pass"] == 2
    )
    prior_texts = [m["text"] for m in player_1_pass_two["prior_messages"]]
    assert "Pass one." in prior_texts
    assert "Pass two." in prior_texts


def test_press_coordinator_multi_pass_fails_hard_with_pass_no() -> None:
    class BrokenClient:
        def complete(self, scene_text: str) -> str:
            return "not json"

    coordinator = PressCoordinator(
        speakers=["player_0"],
        clients={"player_0": BrokenClient()},
        identities={"player_0": {"name": "player_0"}},
        press_sink=[],
        max_retries=0,
        passes=2,
    )

    with pytest.raises(ConcordiaDecisionFailure, match="press message"):
        coordinator.run_round_press(observations=_one_observation(), round_no=2)


def test_full_press_delivers_private_to_sender_and_recipient() -> None:
    class ScriptedClient:
        def __init__(self, responses: list[str]) -> None:
            self.responses = responses
            self.index = 0

        def complete(self, scene_text: str) -> str:
            response = self.responses[self.index]
            self.index += 1
            return response

    sink: list[dict] = []
    whisper = '{"action_id": "whisper", "to": "player_1", "message": "Secret deal."}'
    clients = {
        "player_0": ScriptedClient([whisper]),
        "player_1": FirstLegalConcordiaClient(),
        "player_2": FirstLegalConcordiaClient(),
    }
    coordinator = PressCoordinator(
        speakers=["player_0", "player_1", "player_2"],
        clients=clients,
        identities={pid: {"name": pid} for pid in ["player_0", "player_1", "player_2"]},
        press_sink=sink,
        max_retries=0,
        mode="full_press",
    )

    coordinator.run_round_press(
        observations=_observations(["player_0", "player_1", "player_2"]), round_no=2
    )

    whisper_record = next(r for r in sink if r["speaker"] == "player_0")
    assert whisper_record["visibility"] == "private"
    assert whisper_record["recipient"] == "player_1"
    player_2_record = next(r for r in sink if r["speaker"] == "player_2")
    prior_speakers = [m["speaker"] for m in player_2_record["prior_messages"]]
    assert "player_0" not in prior_speakers or not any(
        m.get("visibility") == "private" for m in player_2_record["prior_messages"]
    )
    player_1_record = next(r for r in sink if r["speaker"] == "player_1")
    player_1_prior = [
        m for m in player_1_record["prior_messages"] if m.get("visibility") == "private"
    ]
    assert len(player_1_prior) == 1


def test_full_press_failure_snapshot_excludes_private_from_nonparticipant() -> None:
    class ScriptedClient:
        def __init__(self, responses: list[str]) -> None:
            self.responses = responses
            self.index = 0

        def complete(self, scene_text: str) -> str:
            response = self.responses[self.index]
            self.index += 1
            return response

    class BrokenClient:
        def complete(self, scene_text: str) -> str:
            return "not json"

    whisper = '{"action_id": "whisper", "to": "player_1", "message": "Secret deal."}'
    clients = {
        "player_0": ScriptedClient([whisper]),
        "player_1": FirstLegalConcordiaClient(),
        "player_2": BrokenClient(),
    }
    coordinator = PressCoordinator(
        speakers=["player_0", "player_1", "player_2"],
        clients=clients,
        identities={pid: {"name": pid} for pid in ["player_0", "player_1", "player_2"]},
        press_sink=[],
        max_retries=0,
        mode="full_press",
    )

    with pytest.raises(ConcordiaDecisionFailure, match="press message") as exc_info:
        coordinator.run_round_press(
            observations=_observations(["player_0", "player_1", "player_2"]),
            round_no=2,
        )

    prior = exc_info.value.snapshot["prior_messages"]
    private_seen = [m for m in prior if m.get("visibility") == "private"]
    assert private_seen == [], "non-participant failure snapshot leaked private message"


def test_press_coordinator_full_press_fails_hard_on_whisper_to_self() -> None:
    class SelfWhisperClient:
        def complete(self, scene_text: str) -> str:
            return '{"action_id": "whisper", "to": "player_0", "message": "Self."}'

    coordinator = PressCoordinator(
        speakers=["player_0"],
        clients={"player_0": SelfWhisperClient()},
        identities={"player_0": {"name": "player_0"}},
        press_sink=[],
        max_retries=0,
        mode="full_press",
    )

    with pytest.raises(ConcordiaDecisionFailure, match="whisper to yourself"):
        coordinator.run_round_press(observations=_one_observation(), round_no=2)


def test_press_coordinator_full_press_fails_hard_on_dead_recipient() -> None:
    class DeadRecipientClient:
        def complete(self, scene_text: str) -> str:
            return (
                '{"action_id": "whisper", "to": "player_9", "message": "To the dead."}'
            )

    coordinator = PressCoordinator(
        speakers=["player_0"],
        clients={"player_0": DeadRecipientClient()},
        identities={"player_0": {"name": "player_0"}},
        press_sink=[],
        max_retries=0,
        mode="full_press",
    )

    with pytest.raises(ConcordiaDecisionFailure, match="not a living player"):
        coordinator.run_round_press(observations=_one_observation(), round_no=2)


class _ScriptedClient:
    def __init__(self, responses: list[str]) -> None:
        self.responses = responses
        self.index = 0

    def complete(self, scene_text: str) -> str:
        response = self.responses[self.index]
        self.index += 1
        return response


_WHISPER = '{"action_id": "whisper", "to": "player_1", "message": "Secret deal."}'


def test_press_light_rejects_whisper_through_retry_feedback() -> None:
    """A whisper in a public-only mode is rejected via the retry-feedback path."""
    coordinator = PressCoordinator(
        speakers=["player_0", "player_1"],
        clients={
            "player_0": _ScriptedClient([_WHISPER]),
            "player_1": FirstLegalConcordiaClient(),
        },
        identities={pid: {"name": pid} for pid in ["player_0", "player_1"]},
        press_sink=[],
        max_retries=0,
        mode="press_light",
    )

    with pytest.raises(ConcordiaDecisionFailure, match="press message") as exc_info:
        coordinator.run_round_press(observations=_two_observations(), round_no=2)

    feedback = exc_info.value.snapshot["validation_errors"]
    assert any("whisper" in error.lower() for error in feedback)


def test_multi_turn_public_rejects_whisper() -> None:
    # Give player_0 enough scripted whispers to cover every pass, so the failure
    # can only come from whisper rejection (pass 1), never from client exhaustion.
    coordinator = PressCoordinator(
        speakers=["player_0", "player_1"],
        clients={
            "player_0": _ScriptedClient([_WHISPER, _WHISPER]),
            "player_1": FirstLegalConcordiaClient(),
        },
        identities={pid: {"name": pid} for pid in ["player_0", "player_1"]},
        press_sink=[],
        max_retries=0,
        passes=2,
        mode="multi_turn_public",
    )

    with pytest.raises(ConcordiaDecisionFailure, match="press message") as exc_info:
        coordinator.run_round_press(observations=_two_observations(), round_no=2)

    feedback = exc_info.value.snapshot["validation_errors"]
    assert any("whisper" in error.lower() for error in feedback)


def test_press_light_whisper_retry_recovers_to_public() -> None:
    """When the retry produces a public message, the run succeeds publicly."""
    sink: list[dict] = []
    coordinator = PressCoordinator(
        speakers=["player_0", "player_1"],
        clients={
            "player_0": _ScriptedClient([_WHISPER, '{"message": "Public now."}']),
            "player_1": FirstLegalConcordiaClient(),
        },
        identities={pid: {"name": pid} for pid in ["player_0", "player_1"]},
        press_sink=sink,
        max_retries=1,
        mode="press_light",
    )

    coordinator.run_round_press(observations=_two_observations(), round_no=2)

    player_0_record = next(r for r in sink if r["speaker"] == "player_0")
    assert player_0_record["text"] == "Public now."
    assert player_0_record["visibility"] == "public"
    assert player_0_record["retries"] == 1


def test_press_light_view_matches_decision_memory_visibility_filter() -> None:
    """The press-scene view carries the same shape as the visible_to filter."""
    from nuclear_war_concordia.press_visibility import visible_to

    sink: list[dict] = []
    coordinator = PressCoordinator(
        speakers=["player_0", "player_1"],
        clients={
            "player_0": _ScriptedClient(['{"message": "Hold fire."}']),
            "player_1": FirstLegalConcordiaClient(),
        },
        identities={pid: {"name": pid} for pid in ["player_0", "player_1"]},
        press_sink=sink,
        max_retries=0,
        mode="press_light",
    )

    transcript = coordinator.run_round_press(
        observations=_two_observations(), round_no=2
    )

    player_1_record = next(r for r in sink if r["speaker"] == "player_1")
    prior = player_1_record["prior_messages"]
    # visible_to (the decision-memory filter) is what the press-scene view must use.
    assert prior == visible_to("player_1", transcript[:1])
    assert all("visibility" in msg for msg in prior)


def test_full_press_whisper_to_self_failure_records_recipient_audience() -> None:
    """The failure snapshot records the attempted message's audience, not 'public'."""

    class SelfWhisperClient:
        def complete(self, scene_text: str) -> str:
            return '{"action_id": "whisper", "to": "player_0", "message": "Self."}'

    coordinator = PressCoordinator(
        speakers=["player_0"],
        clients={"player_0": SelfWhisperClient()},
        identities={"player_0": {"name": "player_0"}},
        press_sink=[],
        max_retries=0,
        mode="full_press",
    )

    with pytest.raises(ConcordiaDecisionFailure) as exc_info:
        coordinator.run_round_press(observations=_one_observation(), round_no=2)

    assert exc_info.value.snapshot["audience"] == "player_0"


def test_exhausted_retry_failure_snapshot_matches_last_sent_prompt() -> None:
    """The failure snapshot's scene must be the prompt actually sent, not a
    re-render carrying feedback the model never saw."""

    class AlwaysWhisperClient:
        def complete(self, scene_text: str) -> str:
            return _WHISPER

    coordinator = PressCoordinator(
        speakers=["player_0", "player_1"],
        clients={
            "player_0": AlwaysWhisperClient(),
            "player_1": FirstLegalConcordiaClient(),
        },
        identities={pid: {"name": pid} for pid in ["player_0", "player_1"]},
        press_sink=[],
        max_retries=1,
        mode="press_light",
    )

    with pytest.raises(ConcordiaDecisionFailure) as exc_info:
        coordinator.run_round_press(observations=_two_observations(), round_no=2)

    snapshot = exc_info.value.snapshot
    scene_json = json.dumps(snapshot["scene_payload"], indent=2, sort_keys=True)
    assert scene_json in snapshot["prompts"][-1], (
        "failure snapshot scene_payload does not match the last prompt sent"
    )


def _observations(player_ids: list[str]):
    from nuclear_war_env.observation import observe
    from nuclear_war_env.setup_game import create_game_state

    state = create_game_state("table", player_count=4, seed=81)
    return [observe(state, pid) for pid in player_ids]
