"""CLI replay postal equipment payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_postal_cruise_launch_missing_warhead(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_cruise_launch_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_cruise_launch:{"card":"cruise","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_cruise_launch"
    payload["actions"][0]["payload"] = {"card": "cruise", "target": "player_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_cruise_launch payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_postal_cruise_drop_extra_target(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_postal_cruise_drop_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_cruise_drop:{"missile":"cruise","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_cruise_drop"
    payload["actions"][0]["payload"] = {"missile": "cruise", "target": "player_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_cruise_drop payload fields are invalid" in captured.err
    )


def test_cli_replay_rejects_postal_cruise_move_missing_target(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_postal_cruise_move_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_cruise_move:{"missile":"cruise"}'
    )
    payload["actions"][0]["action_type"] = "postal_cruise_move"
    payload["actions"][0]["payload"] = {"missile": "cruise"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_cruise_move payload fields are invalid" in captured.err
    )


def test_cli_replay_rejects_postal_space_launch_blank_warhead(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_postal_space_launch_blank_warhead.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_space_platform_launch:{"card":"space_1",'
        '"warheads":["warhead_1",""]}'
    )
    payload["actions"][0]["action_type"] = "postal_space_platform_launch"
    payload["actions"][0]["payload"] = {
        "card": "space_1",
        "warheads": ["warhead_1", ""],
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_space_platform_launch warheads must identify cards"
        in captured.err
    )


def test_cli_replay_rejects_postal_cruise_drop_blank_missile(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_postal_cruise_drop_blank_missile.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = 'player_0:postal_cruise_drop:{"missile":""}'
    payload["actions"][0]["action_type"] = "postal_cruise_drop"
    payload["actions"][0]["payload"] = {"missile": ""}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_cruise_drop missile must identify a missile"
        in captured.err
    )


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
