"""CLI replay postal action payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_postal_defense_action_missing_delivery(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_defense_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_defense:{"attacker":"player_1","card":"card_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_defense"
    payload["actions"][0]["payload"] = {"card": "card_1", "attacker": "player_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 postal_defense payload fields are invalid" in captured.err


def test_cli_replay_rejects_postal_sabotage_action_multiple_targets(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_sabotage_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_sabotage:{"card":"card_1","delivery":"missile_1",'
        '"shuttle":"shuttle_1","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_sabotage"
    payload["actions"][0]["payload"] = {
        "card": "card_1",
        "target": "player_1",
        "delivery": "missile_1",
        "shuttle": "shuttle_1",
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 postal_sabotage payload fields are invalid" in captured.err


def test_cli_replay_rejects_postal_supervirus_pass_extra_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_supervirus_pass_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_supervirus_pass:{"card":"virus","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_supervirus_pass"
    payload["actions"][0]["payload"] = {"target": "player_1", "card": "virus"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_supervirus_pass payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_postal_supervirus_start_missing_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_supervirus_start_payload.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_supervirus_start:{"card":"virus"}'
    )
    payload["actions"][0]["action_type"] = "postal_supervirus_start"
    payload["actions"][0]["payload"] = {"card": "virus"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_supervirus_start payload fields are invalid"
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
