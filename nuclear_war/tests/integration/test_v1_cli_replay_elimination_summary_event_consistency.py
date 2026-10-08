"""CLI replay elimination summary and event consistency tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_elimination_without_player_eliminated_event(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_elimination_without_event.json"
    payload = _valid_replay_payload()
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay elimination player_1 must have a player_eliminated event" in (
        captured.err
    )


def _valid_replay_payload() -> dict:
    return {
        "mode": "table",
        "active_variant": ACTIVE_VARIANT.to_payload(),
        "seed": 3,
        "agent": "heuristic",
        "players": 2,
        "winner": "player_0",
        "turns": 1,
        "termination_reason": "one_player_remaining",
        "eliminations": ["player_1"],
        "final_populations": {"player_0": 30, "player_1": 0},
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
