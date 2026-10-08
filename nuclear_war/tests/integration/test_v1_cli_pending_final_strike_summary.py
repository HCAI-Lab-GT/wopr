"""CLI summarize tests for pending final strike replay evidence."""

from __future__ import annotations

import json
from typing import Any

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_summarize_includes_pending_final_strikes(tmp_path, capsys) -> None:
    replay = tmp_path / "pending_final_strike.json"
    replay.write_text(json.dumps(_replay_payload()), encoding="utf-8")

    code = main(["summarize", str(replay)])

    captured = capsys.readouterr()
    assert code == 0
    summary = json.loads(captured.out)
    assert summary["pending_final_strikes"] is True


def _replay_payload() -> dict[str, Any]:
    return {
        "mode": "postal",
        "active_variant": ACTIVE_VARIANT.to_payload(),
        "seed": 3,
        "agent": "heuristic",
        "players": 2,
        "winner": None,
        "turns": 1,
        "termination_reason": "max_turns",
        "eliminations": ["player_1"],
        "final_populations": {"player_0": 30, "player_1": 0},
        "pending_final_strikes": True,
        "actions": [_action()],
        "events": [_event(), _eliminated_event()],
    }


def _action() -> dict[str, Any]:
    return {
        "turn": 1,
        "player_id": "player_0",
        "action_id": "player_0:pass",
        "action_type": "pass",
        "payload": {},
    }


def _event() -> dict[str, Any]:
    return {
        "turn": 1,
        "event_type": "action_passed",
        "player_id": "player_0",
        "card_id": None,
        "payload": {},
    }


def _eliminated_event() -> dict[str, Any]:
    return {
        "turn": 1,
        "event_type": "player_eliminated",
        "player_id": "player_1",
        "card_id": None,
        "payload": {"by": "player_0"},
    }
