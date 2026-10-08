"""CLI replay postal satellite identity validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_postal_killer_satellite_attack_blank_platform(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_killer_satellite_attack_blank_platform.json"
    payload = _valid_postal_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:postal_killer_satellite_attack:{"platform":"",'
        '"satellite":"satellite_1","target_player":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_killer_satellite_attack"
    payload["actions"][0]["payload"] = {
        "satellite": "satellite_1",
        "target_player": "player_1",
        "platform": "",
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_killer_satellite_attack platform "
        "must identify a platform"
    ) in captured.err


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
