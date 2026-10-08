"""CLI replay cruise event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_cruise_launched_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_cruise_launched_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 cruise_launched payload fields are invalid" in captured.err


def test_cli_replay_rejects_cruise_move_event_boolean_status(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_cruise_move_status.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _cruise_move_event_payload()
    payload["events"][0]["payload"]["status"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 cruise_move status must be a string" in captured.err


def test_cli_replay_rejects_cruise_dropped_event_boolean_loss(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_cruise_dropped_loss.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _cruise_dropped_event_payload()
    payload["events"][0]["payload"]["loss"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 cruise_dropped loss must be an integer" in captured.err


def test_cli_replay_rejects_cruise_drop_failed_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_cruise_drop_failed_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _cruise_drop_failed_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 cruise_drop_failed payload fields are invalid" in captured.err
    )


def _cruise_move_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "cruise_move",
        "player_id": "player_0",
        "card_id": "cruise_1",
        "payload": {"target": "player_1", "status": "moved"},
    }


def _cruise_dropped_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "cruise_dropped",
        "player_id": "player_0",
        "card_id": "cruise_1",
        "payload": {"target": "player_1", "loss": 10, "yield": 10},
    }


def _cruise_drop_failed_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "cruise_drop_failed",
        "player_id": "player_0",
        "card_id": "cruise_1",
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
                "event_type": "cruise_launched",
                "player_id": "player_0",
                "card_id": "cruise_1",
                "payload": {"target": "player_1"},
            }
        ],
    }
