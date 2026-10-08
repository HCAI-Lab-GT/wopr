"""CLI replay space event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_space_platform_launched_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_space_platform_launched_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    expected = "Replay event 0 space_platform_launched payload fields are invalid"
    assert expected in captured.err


def test_cli_replay_rejects_space_platform_dropped_event_boolean_yield(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_space_platform_dropped_yield.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _space_platform_dropped_event_payload()
    payload["events"][0]["payload"]["yield"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    expected = "Replay event 0 space_platform_dropped yield must be an integer"
    assert expected in captured.err


def test_cli_replay_rejects_space_shuttle_reloaded_event_non_list_added(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_space_shuttle_reloaded_added.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _space_shuttle_reloaded_event_payload()
    payload["events"][0]["payload"]["added"] = 20
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 space_shuttle_reloaded added must be a list" in captured.err


def test_cli_replay_rejects_postal_space_platform_drop_event_boolean_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_space_platform_drop_target.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _postal_space_platform_drop_event_payload()
    payload["events"][0]["payload"]["target"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 postal_space_platform_drop_ordered target must be a string"
    ) in captured.err


def test_cli_replay_rejects_postal_space_platform_drop_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_space_platform_drop_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _postal_space_platform_drop_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 postal_space_platform_drop_ordered payload fields are invalid"
    ) in captured.err


def _space_platform_dropped_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "space_platform_dropped",
        "player_id": "player_0",
        "card_id": "platform_1",
        "payload": {"target": "player_1", "loss": 20, "yield": 20},
    }


def _space_shuttle_reloaded_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "space_shuttle_reloaded",
        "player_id": "player_0",
        "card_id": "shuttle_1",
        "payload": {"added": [20]},
    }


def _postal_space_platform_drop_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "postal_space_platform_drop_ordered",
        "player_id": "player_0",
        "card_id": "platform_1",
        "payload": {"target": "player_1"},
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
        "final_populations": {"player_0": 30, "player_1": 10},
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
                "event_type": "space_platform_launched",
                "player_id": "player_0",
                "card_id": "platform_1",
                "payload": {},
            }
        ],
    }
