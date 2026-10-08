"""Press response parsing tests."""

from __future__ import annotations

import pytest

from nuclear_war_concordia.press_response import parse_press_response


def test_parse_press_response_reads_message_and_rationale() -> None:
    parsed = parse_press_response('{"message": "Hold fire.", "rationale": "caution"}')

    assert parsed.text == "Hold fire."
    assert parsed.rationale == "caution"
    assert parsed.is_decline is False


def test_parse_press_response_reads_fenced_message_and_rationale() -> None:
    parsed = parse_press_response(
        '```json\n{"message": "Hold fire.", "rationale": "caution"}\n```'
    )

    assert parsed.text == "Hold fire."
    assert parsed.rationale == "caution"
    assert parsed.is_decline is False


def test_parse_press_response_reads_message_without_rationale() -> None:
    parsed = parse_press_response('{"message": "Hold fire."}')

    assert parsed.text == "Hold fire."
    assert parsed.rationale is None
    assert parsed.is_decline is False


def test_parse_press_response_reads_explicit_decline() -> None:
    parsed = parse_press_response('{"action_id": "decline"}')

    assert parsed.text is None
    assert parsed.is_decline is True


def test_parse_press_response_reads_fenced_decline() -> None:
    parsed = parse_press_response('```json\n{"action_id": "decline"}\n```')

    assert parsed.text is None
    assert parsed.is_decline is True


@pytest.mark.parametrize(
    "raw_response",
    [
        "not json",
        "{}",
        '{"message": ""}',
        '{"message": 17}',
        '{"action_id": "speak"}',
    ],
)
def test_parse_press_response_rejects_invalid(raw_response: str) -> None:
    parsed = parse_press_response(raw_response)

    assert parsed.text is None
    assert parsed.is_decline is False


def test_parse_press_response_reads_whisper_with_recipient() -> None:
    parsed = parse_press_response(
        '{"action_id": "whisper", "to": "player_1", "message": "Secret deal.",'
        ' "rationale": "coordinate"}'
    )

    assert parsed.text == "Secret deal."
    assert parsed.rationale == "coordinate"
    assert parsed.recipient == "player_1"
    assert parsed.visibility == "private"
    assert parsed.is_decline is False


def test_parse_press_response_reads_whisper_with_commitment() -> None:
    parsed = parse_press_response(
        '{"action_id": "whisper", "to": "player_1", "message": "Hold.",'
        ' "commitment": {"kind": "stand_down", "target_round": 3}}'
    )

    assert parsed.recipient == "player_1"
    assert parsed.commitment == {"kind": "stand_down", "target_round": 3}


def test_parse_press_response_reads_speak_with_commitment() -> None:
    parsed = parse_press_response(
        '{"action_id": "speak", "message": "Stand down.",'
        ' "commitment": {"kind": "no_first_use"}}'
    )

    assert parsed.text == "Stand down."
    assert parsed.recipient is None
    assert parsed.visibility == "public"
    assert parsed.commitment == {"kind": "no_first_use"}


@pytest.mark.parametrize(
    "raw_response",
    [
        '{"action_id": "whisper", "message": "no recipient"}',
        '{"action_id": "whisper", "to": "player_1"}',
        '{"action_id": "whisper", "to": "", "message": "empty recipient"}',
        '{"action_id": "whisper", "to": "  ", "message": "blank recipient"}',
        '{"action_id": "whisper", "message": ""}',
    ],
)
def test_parse_press_response_rejects_invalid_whisper(raw_response: str) -> None:
    parsed = parse_press_response(raw_response)

    assert parsed.text is None
    assert parsed.recipient is None
    assert parsed.is_decline is False


def test_parse_press_response_drops_malformed_commitment() -> None:
    parsed = parse_press_response(
        '{"action_id": "speak", "message": "Stand down.", "commitment": {"kind": ""}}'
    )

    assert parsed.text == "Stand down."
    assert parsed.commitment is None
