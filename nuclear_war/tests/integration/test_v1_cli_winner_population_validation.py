"""CLI replay winner-population consistency tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_missing_live_winner(tmp_path, capsys) -> None:
    invalid = tmp_path / "missing_live_winner.json"
    payload = _valid_replay_payload()
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay winner does not match final populations" in captured.err


def test_cli_replay_rejects_experiment_missing_live_winner(tmp_path, capsys) -> None:
    invalid = tmp_path / "missing_experiment_live_winner.json"
    payload = _valid_experiment_payload()
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 winner does not match final populations" in captured.err


def test_cli_replay_rejects_max_turns_leader_as_winner(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_max_turns_winner.json"
    payload = _valid_replay_payload()
    payload["winner"] = "player_1"
    payload["termination_reason"] = "max_turns"
    payload["eliminations"] = []
    payload["final_populations"] = {"player_0": 20, "player_1": 30}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay winner does not match final populations" in captured.err


def test_cli_replay_rejects_experiment_max_turns_leader_as_winner(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_experiment_max_turns_winner.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["winner"] = "player_1"
    payload["results"][0]["termination_reason"] = "max_turns"
    payload["results"][0]["eliminations"] = []
    payload["results"][0]["final_populations"] = {"player_0": 20, "player_1": 30}
    payload["summary"] = {
        "termination_counts": {"max_turns": 1},
        "winner_counts": {"player_1": 1},
        "average_turns": 20.0,
        "total_eliminations": 0,
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 winner does not match final populations" in captured.err


def _valid_replay_payload() -> dict:
    return {
        "mode": "table",
        "active_variant": ACTIVE_VARIANT.to_payload(),
        "seed": 3,
        "agent": "heuristic",
        "players": 2,
        "winner": None,
        "turns": 1,
        "termination_reason": "one_player_remaining",
        "eliminations": ["player_0"],
        "final_populations": {"player_0": 0, "player_1": 30},
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
                "winner": None,
                "turns": 20,
                "eliminations": ["player_0"],
                "final_populations": {"player_0": 0, "player_1": 30},
                "termination_reason": "one_player_remaining",
            }
        ],
        "summary": {
            "termination_counts": {"one_player_remaining": 1},
            "winner_counts": {"no_winner": 1},
            "average_turns": 20.0,
            "total_eliminations": 1,
        },
    }
