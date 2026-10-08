"""CLI replay pending-final-strike schema validation tests."""

from __future__ import annotations

import json
from typing import Any

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_non_boolean_pending_final_strikes(
    tmp_path,
    capsys,
) -> None:
    invalid = tmp_path / "bad_pending_final_strikes.json"
    payload = _replay_payload({"pending_final_strikes": 1})
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay pending_final_strikes must be a boolean" in captured.err


def test_cli_replay_rejects_experiment_non_boolean_pending_final_strikes(
    tmp_path,
    capsys,
) -> None:
    invalid = tmp_path / "bad_result_pending_final_strikes.json"
    payload = _experiment_payload()
    payload["results"][0]["pending_final_strikes"] = 1
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 pending_final_strikes must be a boolean" in captured.err


def test_cli_replay_rejects_decisive_result_with_pending_final_strikes(
    tmp_path,
    capsys,
) -> None:
    invalid = tmp_path / "bad_decisive_pending_final_strikes.json"
    payload = _decisive_replay_payload({"pending_final_strikes": True})
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay pending_final_strikes requires max_turns" in captured.err


def test_cli_replay_rejects_decisive_experiment_result_with_pending_final_strikes(
    tmp_path,
    capsys,
) -> None:
    invalid = tmp_path / "bad_result_decisive_pending_final_strikes.json"
    payload = _experiment_payload()
    payload["results"][0]["pending_final_strikes"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 pending_final_strikes requires max_turns" in captured.err
    )


def _replay_payload(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
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
        "actions": [_action()],
        "events": [_event()],
    }
    if extra:
        payload.update(extra)
    return payload


def _decisive_replay_payload(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    return _replay_payload(
        {
            "winner": "player_1",
            "turns": 20,
            "termination_reason": "one_player_remaining",
            "eliminations": ["player_0"],
            "final_populations": {"player_0": 0, "player_1": 30},
            **(extra or {}),
        }
    )


def _experiment_payload() -> dict[str, Any]:
    result = _decisive_replay_payload()
    for field in ("players", "actions", "events"):
        result.pop(field)
    return {
        "mode": "table",
        "players": 2,
        "seed_start": 3,
        "runs": 1,
        "agent": "heuristic",
        "max_turns": 20,
        "press": False,
        "results": [result],
        "summary": {
            "termination_counts": {"one_player_remaining": 1},
            "winner_counts": {"player_1": 1},
            "average_turns": 20.0,
            "total_eliminations": 1,
        },
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
