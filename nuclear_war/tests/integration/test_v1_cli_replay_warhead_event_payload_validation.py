"""CLI replay warhead event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_warhead_event_boolean_yield(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_warhead_event_yield.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _warhead_event_payload()
    payload["events"][0]["payload"]["yield"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 warhead_detonated yield must be an integer" in captured.err


def test_cli_replay_rejects_player_eliminated_event_numeric_by(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_eliminated_event_by.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _player_eliminated_event_payload()
    payload["events"][0]["payload"]["by"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 player_eliminated by must be a string" in captured.err


def test_cli_replay_rejects_launch_backfire_event_boolean_loss(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_launch_backfire_event_loss.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _launch_backfire_event_payload()
    payload["events"][0]["payload"]["loss"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 launch_backfire loss must be an integer" in captured.err


def test_cli_replay_rejects_warhead_loaded_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_warhead_loaded_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _warhead_loaded_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 warhead_loaded payload fields are invalid" in captured.err


def _warhead_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "warhead_detonated",
        "player_id": "player_0",
        "card_id": None,
        "payload": {"target": "player_1", "yield": 20, "loss": 20},
    }


def _launch_backfire_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "launch_backfire",
        "player_id": "player_0",
        "card_id": None,
        "payload": {"loss": 10},
    }


def _player_eliminated_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "player_eliminated",
        "player_id": "player_1",
        "card_id": None,
        "payload": {"by": "player_0"},
    }


def _warhead_loaded_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "warhead_loaded",
        "player_id": "player_0",
        "card_id": "warhead_1",
        "payload": {"delivery": "delivery_1", "previous": "delivery_1"},
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
