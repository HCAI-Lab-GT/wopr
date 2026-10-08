"""CLI replay string metadata validation tests."""

from __future__ import annotations

import json
from typing import Any

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_non_string_mode(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_mode_type.json"
    payload = _valid_replay_payload()
    payload["mode"] = ["table"]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = _main_without_raw_type_error(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay mode must be a string" in captured.err


def test_cli_replay_rejects_experiment_non_string_agent(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_agent_type.json"
    payload = _valid_experiment_payload()
    payload["agent"] = ["random"]
    payload["results"][0]["agent"] = ["random"]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = _main_without_raw_type_error(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment agent must be a string" in captured.err


def _main_without_raw_type_error(args: list[str]) -> int:
    try:
        return main(args)
    except TypeError:
        return -1


def _valid_replay_payload() -> dict[str, Any]:
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


def _valid_experiment_payload() -> dict[str, Any]:
    return {
        "mode": "table",
        "players": 2,
        "seed_start": 5,
        "runs": 1,
        "agent": "random",
        "max_turns": 50,
        "press": False,
        "results": [
            {
                "seed": 5,
                "mode": "table",
                "active_variant": ACTIVE_VARIANT.to_payload(),
                "agent": "random",
                "winner": "player_1",
                "turns": 20,
                "eliminations": ["player_0"],
                "final_populations": {"player_0": 0, "player_1": 30},
                "termination_reason": "one_player_remaining",
            }
        ],
        "summary": {
            "termination_counts": {"one_player_remaining": 1},
            "winner_counts": {"player_1": 1},
            "average_turns": 20.0,
            "total_eliminations": 1,
        },
    }
