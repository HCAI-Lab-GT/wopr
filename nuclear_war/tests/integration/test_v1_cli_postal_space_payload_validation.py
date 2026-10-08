"""CLI replay postal space payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_postal_space_platform_launch_non_list_warheads(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_space_platform_launch_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_space_platform_launch:{"card":"platform",'
        '"warheads":"warhead_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_space_platform_launch"
    payload["actions"][0]["payload"] = {
        "card": "platform",
        "warheads": "warhead_1",
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_space_platform_launch warheads must be a list"
        in captured.err
    )


def test_cli_replay_rejects_postal_space_shuttle_reload_non_list_warheads(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_space_shuttle_reload_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_space_shuttle_reload:{"card":"shuttle",'
        '"platform":"platform_1","warheads":"warhead_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_space_shuttle_reload"
    payload["actions"][0]["payload"] = {
        "card": "shuttle",
        "platform": "platform_1",
        "warheads": "warhead_1",
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_space_shuttle_reload warheads must be a list"
        in captured.err
    )


def test_cli_replay_rejects_postal_space_shuttle_attack_missing_warhead(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_space_shuttle_attack_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_space_shuttle_attack:{"card":"shuttle","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_space_shuttle_attack"
    payload["actions"][0]["payload"] = {
        "card": "shuttle",
        "target": "player_1",
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_space_shuttle_attack payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_postal_space_platform_drop_missing_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_space_platform_drop_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_space_platform_drop:{"platform":"platform_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_space_platform_drop"
    payload["actions"][0]["payload"] = {"platform": "platform_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_space_platform_drop payload fields are invalid"
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
