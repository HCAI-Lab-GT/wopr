"""CLI replay postal equipment identity validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_postal_cruise_move_blank_missile(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_postal_cruise_move_blank_missile.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_cruise_move:{"missile":"","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_cruise_move"
    payload["actions"][0]["payload"] = {"missile": "", "target": "player_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_cruise_move missile must identify a missile"
        in captured.err
    )


def test_cli_replay_rejects_postal_space_platform_launch_blank_card(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_space_platform_launch_blank_card.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_space_platform_launch:{"card":"","warheads":["warhead_1"]}'
    )
    payload["actions"][0]["action_type"] = "postal_space_platform_launch"
    payload["actions"][0]["payload"] = {"card": "", "warheads": ["warhead_1"]}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_space_platform_launch card must identify a card"
        in captured.err
    )


def test_cli_replay_rejects_postal_space_shuttle_reload_blank_platform(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_space_shuttle_reload_blank_platform.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_space_shuttle_reload:{"card":"shuttle_1",'
        '"platform":"","warheads":["warhead_1"]}'
    )
    payload["actions"][0]["action_type"] = "postal_space_shuttle_reload"
    payload["actions"][0]["payload"] = {
        "card": "shuttle_1",
        "platform": "",
        "warheads": ["warhead_1"],
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_space_shuttle_reload platform must identify a platform"
        in captured.err
    )


def test_cli_replay_rejects_postal_space_shuttle_reload_blank_card(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_space_shuttle_reload_blank_card.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_space_shuttle_reload:{"card":"",'
        '"platform":"platform_1","warheads":["warhead_1"]}'
    )
    payload["actions"][0]["action_type"] = "postal_space_shuttle_reload"
    payload["actions"][0]["payload"] = {
        "card": "",
        "platform": "platform_1",
        "warheads": ["warhead_1"],
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_space_shuttle_reload card must identify a card"
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
