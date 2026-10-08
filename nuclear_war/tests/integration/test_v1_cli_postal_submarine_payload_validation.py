"""CLI replay postal submarine payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_postal_submarine_launch_missing_warhead(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_submarine_launch_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_submarine_launch:{"card":"sub","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_submarine_launch"
    payload["actions"][0]["payload"] = {"card": "sub", "target": "player_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_submarine_launch payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_postal_submarine_reload_missing_warhead(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_submarine_reload_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_submarine_reload:{"submarine":"sub","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_submarine_reload"
    payload["actions"][0]["payload"] = {"submarine": "sub", "target": "player_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_submarine_reload payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_postal_submarine_fire_extra_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_submarine_fire_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_submarine_fire:{"submarine":"sub","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_submarine_fire"
    payload["actions"][0]["payload"] = {"submarine": "sub", "target": "player_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_submarine_fire payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_postal_submarine_return_extra_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_submarine_return_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_submarine_return:{"submarine":"sub","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_submarine_return"
    payload["actions"][0]["payload"] = {"submarine": "sub", "target": "player_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_submarine_return payload fields are invalid"
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
