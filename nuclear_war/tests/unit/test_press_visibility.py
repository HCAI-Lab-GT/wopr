"""Full-press visibility filter tests."""

from __future__ import annotations

from nuclear_war_concordia.press_visibility import visible_to


def _public(turn: int, speaker: str, text: str) -> dict:
    return {
        "turn": turn,
        "speaker": speaker,
        "text": text,
        "audience": "public",
        "visibility": "public",
    }


def _private(turn: int, speaker: str, recipient: str, text: str) -> dict:
    return {
        "turn": turn,
        "speaker": speaker,
        "recipient": recipient,
        "text": text,
        "audience": recipient,
        "visibility": "private",
    }


def test_visible_to_returns_all_public_messages_to_any_player() -> None:
    transcript = [
        _public(1, "player_0", "Hold fire."),
        _public(1, "player_1", "Stand down."),
    ]

    assert visible_to("player_2", transcript) == transcript


def test_visible_to_returns_private_only_to_sender_and_recipient() -> None:
    transcript = [_private(1, "player_0", "player_1", "Secret deal.")]

    assert visible_to("player_0", transcript) == transcript
    assert visible_to("player_1", transcript) == transcript
    assert visible_to("player_2", transcript) == []


def test_visible_to_excludes_private_messages_between_other_players() -> None:
    transcript = [
        _public(1, "player_0", "Public."),
        _private(1, "player_1", "player_2", "Between us only."),
        _private(2, "player_2", "player_1", "Agreed."),
    ]

    view = visible_to("player_3", transcript)

    assert view == [_public(1, "player_0", "Public.")]


def test_visible_to_returns_empty_for_player_with_no_visible_messages() -> None:
    transcript = [_private(1, "player_0", "player_1", "Just us.")]

    assert visible_to("player_3", transcript) == []


def test_visible_to_does_not_mutate_input_messages() -> None:
    transcript = [_private(1, "player_0", "player_1", "Secret.")]
    original = [dict(message) for message in transcript]

    visible_to("player_0", transcript)

    assert transcript == original


def test_visible_to_copies_returned_messages() -> None:
    transcript = [_public(1, "player_0", "Public.")]
    view = visible_to("player_0", transcript)

    view[0]["text"] = "mutated"
    assert transcript[0]["text"] == "Public."
