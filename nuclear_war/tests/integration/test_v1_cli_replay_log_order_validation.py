"""CLI replay log ordering validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_action_log_with_decreasing_turns(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_order.json"
    payload = _valid_replay_payload()
    payload["actions"] = [
        _action(turn=2, player_id="player_1"),
        _action(turn=1, player_id="player_0"),
    ]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action log turns must be nondecreasing" in captured.err


def test_cli_replay_rejects_event_log_with_decreasing_turns(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_event_order.json"
    payload = _valid_replay_payload()
    payload["events"] = [
        _event(turn=2, player_id="player_1"),
        _event(turn=1, player_id="player_0"),
    ]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event log turns must be nondecreasing" in captured.err


def _action(turn: int, player_id: str) -> dict:
    return {
        "turn": turn,
        "player_id": player_id,
        "action_id": f"{player_id}:pass",
        "action_type": "pass",
        "payload": {},
    }


def _event(turn: int, player_id: str) -> dict:
    return {
        "turn": turn,
        "event_type": "action_passed",
        "player_id": player_id,
        "card_id": None,
        "payload": {},
    }


def _valid_replay_payload() -> dict:
    return {
        "mode": "table",
        "active_variant": ACTIVE_VARIANT.to_payload(),
        "seed": 3,
        "agent": "heuristic",
        "players": 2,
        "winner": None,
        "turns": 2,
        "termination_reason": "max_turns",
        "eliminations": [],
        "final_populations": {"player_0": 30, "player_1": 30},
        "actions": [_action(turn=1, player_id="player_0")],
        "events": [_event(turn=1, player_id="player_0")],
    }
