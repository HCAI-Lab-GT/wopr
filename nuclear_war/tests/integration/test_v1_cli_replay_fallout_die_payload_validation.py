"""CLI replay validation for the postal Radioactive Fallout die event."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_accepts_valid_fallout_die_event(tmp_path, capsys) -> None:
    valid = tmp_path / "good_fallout_die.json"
    payload = _valid_postal_replay_payload()
    payload["events"].append(_fallout_die_event())
    valid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(valid)])
    captured = capsys.readouterr()
    assert code == 0, captured.err


def test_cli_replay_rejects_fallout_die_event_in_table_replay(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_table_fallout_die.json"
    payload = _valid_postal_replay_payload()
    payload["mode"] = "table"
    payload["events"].append(_fallout_die_event())
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "requires postal mode" in captured.err


def test_cli_replay_rejects_fallout_die_event_out_of_range_roll(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_fallout_die_roll.json"
    payload = _valid_postal_replay_payload()
    event = _fallout_die_event()
    event["payload"]["raw_result"] = 7
    payload["events"].append(event)
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "fallout_die raw_result must be between 1 and 6" in captured.err


def test_cli_replay_rejects_fallout_die_event_cloud_mismatch(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_fallout_die_cloud.json"
    payload = _valid_postal_replay_payload()
    event = _fallout_die_event()
    event["payload"]["raw_result"] = 4
    event["payload"]["cloud"] = True
    payload["events"].append(event)
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "fallout_die cloud does not match raw_result" in captured.err


def test_cli_replay_rejects_fallout_die_event_wrong_source_table(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_fallout_die_source.json"
    payload = _valid_postal_replay_payload()
    event = _fallout_die_event()
    event["payload"]["source_table_id"] = "base_two_d10_fallout_chart"
    payload["events"].append(event)
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "fallout_die source_table_id has invalid value" in captured.err


def test_cli_replay_rejects_fallout_die_event_extra_field(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_fallout_die_extra.json"
    payload = _valid_postal_replay_payload()
    event = _fallout_die_event()
    event["payload"]["effect"] = "no_radiation"
    payload["events"].append(event)
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "fallout_die payload fields are invalid" in captured.err


def _fallout_die_event() -> dict:
    return {
        "turn": 1,
        "event_type": "fallout_die_result",
        "player_id": "player_0",
        "card_id": "platform_1",
        "payload": {
            "raw_result": 4,
            "cloud": False,
            "randomizer": "postal_radioactive_fallout_die",
            "source_table_id": "postal_radioactive_fallout_die",
        },
    }


def _valid_postal_replay_payload() -> dict:
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
