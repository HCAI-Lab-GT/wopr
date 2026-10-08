from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_incomplete_event_log_entry(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_event_entry.json"
    payload = _valid_replay_payload()
    payload["events"] = [{"turn": 1, "player_id": "player_0"}]
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 missing required field: event_type" in captured.err


def test_cli_replay_rejects_action_turn_before_game_start(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_turn.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["turn"] = 0
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 has invalid turn: 0" in captured.err


def test_cli_replay_rejects_action_without_string_player_id(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_player.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["player_id"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 player_id must be a string" in captured.err


def test_cli_replay_rejects_event_turn_after_game_end(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_event_turn.json"
    payload = _valid_replay_payload()
    payload["events"][0]["turn"] = 2
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 has invalid turn: 2" in captured.err


def test_cli_replay_rejects_action_without_string_action_id(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_id.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 action_id must be a string" in captured.err


def test_cli_replay_rejects_action_without_string_action_type(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_type.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_type"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 action_type must be a string" in captured.err


def test_cli_replay_rejects_action_without_payload_object(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_payload.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["payload"] = "pass"
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 payload must be an object" in captured.err


def test_cli_replay_rejects_event_without_string_event_type(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_event_type.json"
    payload = _valid_replay_payload()
    payload["events"][0]["event_type"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 event_type must be a string" in captured.err


def test_cli_replay_rejects_event_without_string_player_id(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_event_player.json"
    payload = _valid_replay_payload()
    payload["events"][0]["player_id"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 player_id must be a string or null" in captured.err


def test_cli_replay_rejects_event_without_payload_object(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_event_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"] = "passed"
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 payload must be an object" in captured.err


def _valid_replay_payload() -> dict:
    return {
        "mode": "table",
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
