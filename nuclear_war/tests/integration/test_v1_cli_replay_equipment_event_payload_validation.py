"""CLI replay equipment event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_equipment_destroyed_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_equipment_destroyed_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 equipment_destroyed payload fields are invalid" in captured.err
    )


def test_cli_replay_rejects_equipment_target_missed_event_boolean_target_player(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_equipment_target_missed_target_player.json"
    payload = _valid_replay_payload()
    payload["events"][0]["event_type"] = "equipment_target_missed"
    payload["events"][0]["payload"]["target_player"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 equipment_target_missed target_player must be a string"
        in captured.err
    )


def test_cli_replay_rejects_equipment_destroyed_event_blank_equipment(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_equipment_destroyed_blank_equipment.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["equipment"] = ""
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 equipment_destroyed equipment must identify equipment"
        in captured.err
    )


def test_cli_replay_rejects_equipment_target_failed_event_boolean_reason(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_equipment_target_failed_reason.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _equipment_target_failed_event_payload()
    payload["events"][0]["payload"]["reason"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 equipment_target_failed reason must be a string" in captured.err
    )


def _equipment_target_failed_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "equipment_target_failed",
        "player_id": "player_0",
        "card_id": "delivery_1",
        "payload": {"reason": "invalid_equipment_target"},
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
                "event_type": "equipment_destroyed",
                "player_id": "player_0",
                "card_id": "delivery_1",
                "payload": {
                    "target_player": "player_1",
                    "kind": "atomic_cannon",
                    "equipment": "atomic_cannon_1",
                },
            }
        ],
    }
