"""CLI replay validation tests for boolean numeric values."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_boolean_seed(tmp_path, capsys) -> None:
    invalid = tmp_path / "boolean_seed.json"
    payload = _replay_payload()
    payload["seed"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay seed must be an integer" in captured.err


def test_cli_replay_rejects_boolean_action_turn(tmp_path, capsys) -> None:
    invalid = tmp_path / "boolean_action_turn.json"
    payload = _replay_payload()
    payload["actions"][0]["turn"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 has invalid turn: True" in captured.err


def test_cli_replay_rejects_boolean_experiment_runs(tmp_path, capsys) -> None:
    invalid = tmp_path / "boolean_experiment_runs.json"
    payload = _experiment_payload()
    payload["runs"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment has invalid runs: True" in captured.err


def test_cli_replay_rejects_boolean_experiment_result_seed(tmp_path, capsys) -> None:
    invalid = tmp_path / "boolean_experiment_result_seed.json"
    payload = _experiment_payload()
    payload["seed_start"] = 1
    payload["results"][0]["seed"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 seed must be an integer" in captured.err


def test_cli_replay_rejects_boolean_experiment_population(tmp_path, capsys) -> None:
    invalid = tmp_path / "boolean_experiment_population.json"
    payload = _experiment_payload()
    payload["results"][0]["final_populations"]["player_0"] = False
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 final_populations player_0 must be an integer"
        in captured.err
    )


def _replay_payload() -> dict:
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


def _experiment_payload() -> dict:
    result = {
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
    return {
        "mode": "table",
        "players": 2,
        "seed_start": 5,
        "runs": 1,
        "agent": "random",
        "max_turns": 50,
        "press": False,
        "results": [result],
        "summary": {
            "termination_counts": {"one_player_remaining": 1},
            "winner_counts": {"player_1": 1},
            "average_turns": 20.0,
            "total_eliminations": 1,
        },
    }
