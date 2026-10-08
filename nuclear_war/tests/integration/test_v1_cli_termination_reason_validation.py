"""CLI replay termination reason validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_invalid_single_game_termination_reason(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_replay_reason.json"
    payload = _valid_replay_payload()
    payload["termination_reason"] = "timeout"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay termination_reason has invalid value: timeout" in captured.err


def test_cli_replay_rejects_contradictory_single_game_termination_reason(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_replay_reason_population.json"
    payload = _valid_replay_payload()
    payload["winner"] = "player_1"
    payload["eliminations"] = ["player_0"]
    payload["final_populations"] = {"player_0": 0, "player_1": 30}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay termination_reason does not match final populations" in captured.err


def test_cli_replay_rejects_invalid_experiment_termination_reason(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_experiment_reason.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["termination_reason"] = "timeout"
    payload["summary"]["termination_counts"] = {"timeout": 1}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 termination_reason has invalid value: timeout"
        in captured.err
    )


def test_cli_replay_rejects_contradictory_experiment_termination_reason(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_experiment_reason_population.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["termination_reason"] = "max_turns"
    payload["summary"]["termination_counts"] = {"max_turns": 1}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 termination_reason does not match final populations"
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
                "event_type": "action_passed",
                "player_id": "player_0",
                "card_id": None,
                "payload": {},
            }
        ],
    }


def _valid_experiment_payload() -> dict:
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
