"""CLI replay postal atomic cannon payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_postal_atomic_cannon_setup_missing_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_atomic_cannon_setup_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_atomic_cannon_setup:{"card":"cannon"}'
    )
    payload["actions"][0]["action_type"] = "postal_atomic_cannon_setup"
    payload["actions"][0]["payload"] = {"card": "cannon"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_atomic_cannon_setup payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_postal_atomic_cannon_fire_missing_warhead(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_atomic_cannon_fire_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_atomic_cannon_fire:{"cannon":"cannon_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_atomic_cannon_fire"
    payload["actions"][0]["payload"] = {"cannon": "cannon_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_atomic_cannon_fire payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_postal_atomic_cannon_reposition_missing_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_atomic_cannon_reposition_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_atomic_cannon_reposition:{"cannon":"cannon_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_atomic_cannon_reposition"
    payload["actions"][0]["payload"] = {"cannon": "cannon_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_atomic_cannon_reposition payload fields are invalid"
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
