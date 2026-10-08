"""CLI replay event schema validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_event_without_string_or_null_card_id(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_event_card.json"
    payload = _valid_replay_payload()
    payload["events"][0]["card_id"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 card_id must be a string or null" in captured.err


def test_cli_replay_rejects_unknown_event_type(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_event_name.json"
    payload = _valid_replay_payload()
    payload["events"][0]["event_type"] = "invented_event"
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 event_type has invalid value: invented_event" in captured.err


def test_cli_replay_rejects_postal_event_in_table_replay(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_table_postal_event.json"
    payload = _valid_replay_payload()
    payload["events"][0]["event_type"] = "postal_propaganda_ordered"
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 event_type requires postal mode" in captured.err


def test_cli_replay_rejects_spinner_event_missing_source_table(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_spinner_event.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "spinner_result",
        "player_id": "player_0",
        "card_id": None,
        "payload": {
            "raw_result": 10,
            "effect": "normal",
            "multiplier": 1,
            "target_adjustment": 0,
            "randomizer": "base_two_d10_fallout_chart",
        },
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 spinner payload missing source_table_id" in captured.err


def test_cli_replay_rejects_spinner_event_out_of_range_roll(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_spinner_roll.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _spinner_event_payload()
    payload["events"][0]["payload"]["raw_result"] = 100
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 spinner raw_result must be between 0 and 99" in captured.err


def test_cli_replay_rejects_spinner_event_wrong_source_table(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_spinner_source.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _spinner_event_payload()
    payload["events"][0]["payload"]["source_table_id"] = "classic_spinner"
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 spinner source_table_id has invalid value" in captured.err


def _spinner_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "spinner_result",
        "player_id": "player_0",
        "card_id": None,
        "payload": {
            "raw_result": 10,
            "effect": "shelter_saves",
            "multiplier": 1,
            "target_adjustment": -2,
            "randomizer": "base_two_d10_fallout_chart",
            "source_table_id": "base_two_d10_fallout_chart",
        },
    }


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
