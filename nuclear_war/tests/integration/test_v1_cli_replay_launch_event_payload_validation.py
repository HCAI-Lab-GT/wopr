"""CLI replay launch event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_launch_event_string_warheads(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_launch_event_warheads.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _launch_event_payload()
    payload["events"][0]["payload"]["warheads"] = "warhead_1"
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 launch_declared warheads must be a list" in captured.err


def test_cli_replay_rejects_launch_event_blank_warhead(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_launch_event_blank_warhead.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _launch_event_payload()
    payload["events"][0]["payload"]["warheads"] = [""]
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 launch_declared warheads must identify cards" in captured.err


def test_cli_replay_rejects_target_event_numeric_target(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_target_event_target.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _target_event_payload()
    payload["events"][0]["payload"]["target"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 target_declared target must be a string" in captured.err


def test_cli_replay_rejects_intercept_success_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_intercept_success_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _intercept_success_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 intercept_success payload fields are invalid" in captured.err


def test_cli_replay_rejects_intercept_success_event_boolean_stopped_delivery(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_intercept_success_stopped_delivery.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _intercept_success_event_payload()
    payload["events"][0]["payload"]["stopped_delivery"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 intercept_success stopped_delivery must be a string"
        in captured.err
    )


def _launch_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "launch_declared",
        "player_id": "player_0",
        "card_id": "delivery_1",
        "payload": {"target": "player_1", "warheads": ["warhead_1"], "yield": 20},
    }


def _target_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "target_declared",
        "player_id": "player_0",
        "card_id": "delivery_1",
        "payload": {"target": "player_1"},
    }


def _intercept_success_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "intercept_success",
        "player_id": "player_1",
        "card_id": "anti_missile_1",
        "payload": {"stopped_delivery": "delivery_1"},
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
