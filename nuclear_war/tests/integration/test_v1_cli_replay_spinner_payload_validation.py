"""CLI replay spinner payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_spinner_event_extra_payload_field(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_spinner_extra_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _spinner_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 spinner payload fields are invalid" in captured.err


def test_cli_replay_accepts_spinner_acceptance_payload_names(tmp_path, capsys) -> None:
    replay = tmp_path / "spinner_acceptance_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _spinner_event_payload()
    replay.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(replay)])

    captured = capsys.readouterr()
    assert code == 0
    assert captured.err == ""


def test_cli_replay_rejects_spinner_float_multiplier(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_spinner_multiplier.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _spinner_event_payload()
    payload["events"][0]["payload"]["multiplier"] = 1.0
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 spinner multiplier must be an integer" in captured.err


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
