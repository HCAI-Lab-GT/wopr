"""Press trace construction tests."""

from __future__ import annotations

from nuclear_war_agents import LLMCompletion
from nuclear_war_concordia.press_trace import append_press_trace
from nuclear_war_concordia.types import ConcordiaScene, ParsedPressMessage


def test_append_press_trace_writes_full_parity_message_record() -> None:
    sink: list[dict] = []
    scene = ConcordiaScene(text="scene", payload={"player_id": "player_0", "turn": 2})
    completions = [
        LLMCompletion(
            raw_response='{"message": "Hold fire."}',
            provider_latency_ms=12,
            provider_cost=0.02,
            provider_usage={"total_tokens": 7},
            provider_label="together",
            provider_model="demo-1",
        )
    ]

    append_press_trace(
        press_sink=sink,
        round_no=2,
        speaker="player_0",
        audience="public",
        visibility="public",
        pass_no=1,
        prior_messages=[],
        scene=scene,
        prompts=["prompt"],
        raw_responses=['{"message": "Hold fire."}'],
        completions=completions,
        validation_errors=[],
        parsed=ParsedPressMessage(text="Hold fire.", rationale="caution"),
    )

    assert len(sink) == 1
    record = sink[0]
    assert record["message_id"] == "press:2:player_0:1"
    assert record["turn"] == 2
    assert record["round"] == 2
    assert record["speaker"] == "player_0"
    assert record["audience"] == "public"
    assert record["visibility"] == "public"
    assert record["pass"] == 1
    assert record["decision_type"] == "press"
    assert record["text"] == "Hold fire."
    assert record["stated_rationale"] == "caution"
    assert "selected_action_id" not in record
    assert record["provider_label"] == "together"
    assert record["linked_decision_traces"] == []


def test_append_press_trace_records_decline_without_text() -> None:
    sink: list[dict] = []
    scene = ConcordiaScene(text="scene", payload={"player_id": "player_1", "turn": 2})

    append_press_trace(
        press_sink=sink,
        round_no=2,
        speaker="player_1",
        audience="public",
        visibility="public",
        pass_no=1,
        prior_messages=[],
        scene=scene,
        prompts=["prompt"],
        raw_responses=['{"action_id": "decline"}'],
        completions=[],
        validation_errors=[],
        parsed=ParsedPressMessage(declined=True),
    )

    assert sink[0]["text"] is None
    assert sink[0]["parse_result"]["declined"] is True


def test_append_press_trace_is_noop_when_sink_is_none() -> None:
    result = append_press_trace(
        press_sink=None,
        round_no=1,
        speaker="player_0",
        audience="public",
        visibility="public",
        pass_no=1,
        prior_messages=[],
        scene=ConcordiaScene(text="t", payload={}),
        prompts=["p"],
        raw_responses=["r"],
        completions=[],
        validation_errors=[],
        parsed=ParsedPressMessage(),
    )
    assert result is None


def test_append_press_trace_records_private_recipient() -> None:
    sink: list[dict] = []
    scene = ConcordiaScene(text="scene", payload={"player_id": "player_0", "turn": 2})

    append_press_trace(
        press_sink=sink,
        round_no=2,
        speaker="player_0",
        audience="player_1",
        visibility="private",
        pass_no=1,
        prior_messages=[],
        scene=scene,
        prompts=["prompt"],
        raw_responses=['{"action_id": "whisper", "to": "player_1", "message": "x"}'],
        completions=[],
        validation_errors=[],
        parsed=ParsedPressMessage(text="x", recipient="player_1"),
    )

    assert sink[0]["recipient"] == "player_1"
    assert sink[0]["visibility"] == "private"
    assert sink[0]["audience"] == "player_1"


def test_append_press_trace_omits_recipient_for_public_message() -> None:
    sink: list[dict] = []
    scene = ConcordiaScene(text="scene", payload={"player_id": "player_0", "turn": 2})

    append_press_trace(
        press_sink=sink,
        round_no=2,
        speaker="player_0",
        audience="public",
        visibility="public",
        pass_no=1,
        prior_messages=[],
        scene=scene,
        prompts=["prompt"],
        raw_responses=['{"message": "Public."}'],
        completions=[],
        validation_errors=[],
        parsed=ParsedPressMessage(text="Public."),
    )

    assert "recipient" not in sink[0]


def test_append_press_trace_records_commitment_when_present() -> None:
    sink: list[dict] = []
    scene = ConcordiaScene(text="scene", payload={"player_id": "player_0", "turn": 2})
    commitment = {"kind": "stand_down", "target_round": 3}

    append_press_trace(
        press_sink=sink,
        round_no=2,
        speaker="player_0",
        audience="public",
        visibility="public",
        pass_no=1,
        prior_messages=[],
        scene=scene,
        prompts=["prompt"],
        raw_responses=['{"message": "Hold."}'],
        completions=[],
        validation_errors=[],
        parsed=ParsedPressMessage(text="Hold.", commitment=commitment),
    )

    assert sink[0]["commitment"] == commitment


def test_append_press_trace_omits_commitment_when_absent() -> None:
    sink: list[dict] = []
    scene = ConcordiaScene(text="scene", payload={"player_id": "player_0", "turn": 2})

    append_press_trace(
        press_sink=sink,
        round_no=2,
        speaker="player_0",
        audience="public",
        visibility="public",
        pass_no=1,
        prior_messages=[],
        scene=scene,
        prompts=["prompt"],
        raw_responses=['{"message": "Hold."}'],
        completions=[],
        validation_errors=[],
        parsed=ParsedPressMessage(text="Hold."),
    )

    assert "commitment" not in sink[0]
