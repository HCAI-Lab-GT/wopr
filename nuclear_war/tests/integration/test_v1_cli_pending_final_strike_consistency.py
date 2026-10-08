"""CLI replay pending-final-strike consistency tests."""

from __future__ import annotations

import json
from typing import Any

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_pending_without_elimination(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_pending_without_elimination.json"
    payload = _replay_payload()
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay pending_final_strikes requires an elimination" in captured.err


def test_cli_replay_rejects_table_pending(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_table_pending_final_strike.json"
    payload = _replay_payload_with_elimination()
    payload["mode"] = "table"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay pending_final_strikes requires postal mode" in captured.err


def test_cli_replay_rejects_experiment_pending_without_elimination(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_result_pending_without_elimination.json"
    payload = _experiment_payload()
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 pending_final_strikes requires an elimination"
        in captured.err
    )


def test_cli_replay_rejects_experiment_table_pending(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_table_pending_final_strike.json"
    payload = _experiment_payload_with_elimination()
    payload["mode"] = "table"
    payload["results"][0]["mode"] = "table"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 pending_final_strikes requires postal mode" in captured.err
    )


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
        "eliminations": [],
        "final_populations": {"player_0": 30, "player_1": 30},
        "pending_final_strikes": True,
        "actions": [_action()],
        "events": [_event()],
    }


def _replay_payload_with_elimination() -> dict[str, Any]:
    payload = _replay_payload()
    payload["eliminations"] = ["player_1"]
    payload["final_populations"] = {"player_0": 30, "player_1": 0}
    return payload


def _experiment_payload() -> dict[str, Any]:
    result = _replay_payload()
    for field in ("players", "actions", "events"):
        result.pop(field)
    return {
        "mode": "postal",
        "players": 2,
        "seed_start": 3,
        "runs": 1,
        "agent": "heuristic",
        "max_turns": 1,
        "press": False,
        "results": [result],
        "summary": {
            "termination_counts": {"max_turns": 1},
            "winner_counts": {"no_winner": 1},
            "average_turns": 1.0,
            "total_eliminations": 0,
        },
    }


def _experiment_payload_with_elimination() -> dict[str, Any]:
    payload = _experiment_payload()
    result = payload["results"][0]
    result["eliminations"] = ["player_1"]
    result["final_populations"] = {"player_0": 30, "player_1": 0}
    payload["summary"]["total_eliminations"] = 1
    return payload


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
