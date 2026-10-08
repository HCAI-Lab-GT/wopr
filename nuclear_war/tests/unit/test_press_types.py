"""Press message type tests."""

from __future__ import annotations

from nuclear_war_concordia.types import ParsedPressMessage, PressMessage


def test_parsed_press_message_defaults_to_decline() -> None:
    parsed = ParsedPressMessage()

    assert parsed.text is None
    assert parsed.rationale is None
    assert parsed.is_decline is False


def test_parsed_press_message_explicit_decline() -> None:
    parsed = ParsedPressMessage(declined=True)

    assert parsed.is_decline is True


def test_parsed_press_message_with_text_is_not_decline() -> None:
    parsed = ParsedPressMessage(text="Hold fire.", rationale="caution")

    assert parsed.text == "Hold fire."
    assert parsed.rationale == "caution"
    assert parsed.is_decline is False


def test_parsed_press_message_public_when_no_recipient() -> None:
    parsed = ParsedPressMessage(text="Hold fire.")

    assert parsed.recipient is None
    assert parsed.visibility == "public"


def test_parsed_press_message_private_when_recipient_set() -> None:
    parsed = ParsedPressMessage(text="Hold fire.", recipient="player_1")

    assert parsed.recipient == "player_1"
    assert parsed.visibility == "private"


def test_parsed_press_message_carries_commitment() -> None:
    commitment = {"kind": "stand_down", "target_round": 3}
    parsed = ParsedPressMessage(text="Hold fire.", commitment=commitment)

    assert parsed.commitment == commitment


def test_press_message_carries_forward_looking_fields() -> None:
    message = PressMessage(
        message_id="press:2:player_0:1",
        turn=2,
        round_no=2,
        speaker="player_0",
        audience="public",
        visibility="public",
        pass_no=1,
        text="Hold fire.",
        is_decline=False,
    )

    assert message.audience == "public"
    assert message.visibility == "public"
    assert message.pass_no == 1
