"""CLI replay empty event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_special_played_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_special_played_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _special_played_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 special_played payload fields are invalid" in captured.err


def test_cli_replay_rejects_action_passed_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_action_passed_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 action_passed payload fields are invalid" in captured.err


def test_cli_replay_rejects_peace_restored_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_peace_restored_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "peace_restored",
        "player_id": None,
        "card_id": None,
        "payload": {"extra": True},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 peace_restored payload fields are invalid" in captured.err


def test_cli_replay_rejects_card_drawn_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_card_drawn_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "card_drawn",
        "player_id": "player_0",
        "card_id": "warhead_1",
        "payload": {"extra": True},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 card_drawn payload fields are invalid" in captured.err


def test_cli_replay_rejects_secret_queued_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_secret_queued_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "secret_queued",
        "player_id": "player_0",
        "card_id": "secret_1",
        "payload": {"extra": True},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 secret_queued payload fields are invalid" in captured.err


def _special_played_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "special_played",
        "player_id": "player_0",
        "card_id": "special_1",
        "payload": {},
    }


def _valid_replay_payload() -> dict:
    return {
        "mode": "postal",
        "active_variant": ACTIVE_VARIANT.to_payload(),
        "seed": 3,
        "agent": "heuristic",
        "players": 2,
        "winner": None,
        "turns": 1,
        "termination_reason": "max_turns",
        "eliminations": [],
        "final_populations": {"player_0": 30, "player_1": 30},
        "actions": [
            {
                "turn": 1,
                "player_id": "player_0",
                "action_id": "player_0:pass",
                "action_type": "pass",
                "payload": {},
            }
        ],
        "events": [
            {
                "turn": 1,
                "event_type": "action_passed",
                "player_id": "player_0",
                "card_id": None,
                "payload": {},
            }
        ],
    }
