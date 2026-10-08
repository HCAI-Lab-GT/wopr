"""CLI replay launch event identity validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_intercept_success_event_blank_stopped_delivery(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_intercept_success_blank_stopped_delivery.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["stopped_delivery"] = ""
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 intercept_success stopped_delivery must identify a card"
        in captured.err
    )


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
                "event_type": "intercept_success",
                "player_id": "player_1",
                "card_id": "anti_missile_1",
                "payload": {"stopped_delivery": "delivery_1"},
            }
        ],
    }
