"""CLI replay killer satellite event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_killer_satellite_launched_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_killer_satellite_launched_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 killer_satellite_launched payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_killer_satellite_destroyed_platform_boolean_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_killer_satellite_destroyed_platform_target.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _killer_satellite_destroyed_platform_event_payload()
    payload["events"][0]["payload"]["target_player"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 killer_satellite_destroyed_platform "
        "target_player must be a string"
    ) in captured.err


def test_cli_replay_rejects_postal_killer_satellite_attack_event_boolean_platform(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_killer_satellite_attack_platform.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _postal_killer_satellite_attack_event_payload()
    payload["events"][0]["payload"]["platform"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 postal_killer_satellite_attack_ordered "
        "platform must be a string"
    ) in captured.err


def test_cli_replay_rejects_killer_satellite_destroyed_platform_blank_platform(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_killer_satellite_destroyed_platform_blank_platform.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _killer_satellite_destroyed_platform_event_payload()
    payload["events"][0]["payload"]["platform"] = ""
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 killer_satellite_destroyed_platform "
        "platform must identify a platform"
    ) in captured.err


def _killer_satellite_destroyed_platform_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "killer_satellite_destroyed_platform",
        "player_id": "player_0",
        "card_id": "satellite_1",
        "payload": {"target_player": "player_1", "platform": "platform_1"},
    }


def _postal_killer_satellite_attack_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "postal_killer_satellite_attack_ordered",
        "player_id": "player_0",
        "card_id": "satellite_1",
        "payload": {"target_player": "player_1", "platform": "platform_1"},
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
                "event_type": "killer_satellite_launched",
                "player_id": "player_0",
                "card_id": "satellite_1",
                "payload": {},
            }
        ],
    }
