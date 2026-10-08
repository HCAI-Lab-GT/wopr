"""CLI replay action payload player-reference validation tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_env.action_models import payload_suffix
from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


@pytest.mark.parametrize(
    ("action_type", "payload", "expected"),
    [
        ("target", {"delivery": "delivery", "target": "rogue"}, "target"),
        ("final_strike_target", {"target": "rogue"}, "target"),
        (
            "postal_defense",
            {"card": "defense", "attacker": "rogue", "delivery": "delivery"},
            "attacker",
        ),
        (
            "postal_killer_satellite_attack",
            {"satellite": "satellite", "target_player": "rogue", "platform": "p"},
            "target_player",
        ),
    ],
)
def test_cli_replay_rejects_action_payload_unknown_player_reference(
    tmp_path, capsys, action_type: str, payload: dict, expected: str
) -> None:
    invalid = tmp_path / f"bad_{action_type}_{expected}.json"
    replay = _valid_replay_payload()
    replay["mode"] = "postal" if action_type.startswith("postal_") else "table"
    replay["actions"][0] = {
        "turn": 1,
        "player_id": "player_0",
        "action_id": f"player_0:{action_type}{payload_suffix(payload)}",
        "action_type": action_type,
        "payload": payload,
    }
    invalid.write_text(json.dumps(replay), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        f"Replay action 0 {action_type} {expected} must be a known player id"
        in captured.err
    )


def test_cli_replay_rejects_action_payload_self_target(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_self_target.json"
    payload = {"delivery": "delivery", "target": "player_0"}
    replay = _valid_replay_payload()
    replay["actions"][0] = {
        "turn": 1,
        "player_id": "player_0",
        "action_id": f"player_0:target{payload_suffix(payload)}",
        "action_type": "target",
        "payload": payload,
    }
    invalid.write_text(json.dumps(replay), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 target target must not be the acting player" in captured.err


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
