"""CLI experiment replay validation tests for Nuclear War v1."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_experiment_result_count_mismatch(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_count.json"
    payload = _valid_experiment_payload()
    payload["runs"] = 2
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result count 1 does not match runs: 2" in captured.err


def test_cli_replay_rejects_experiment_result_mode_mismatch(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_mode.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["mode"] = "postal"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 mode postal does not match batch mode: table" in (
        captured.err
    )


def test_cli_replay_rejects_experiment_result_non_string_mode(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_result_mode_type.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["mode"] = ["table"]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 mode must be a string" in captured.err


def test_cli_replay_rejects_experiment_result_agent_mismatch(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_agent.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["agent"] = "heuristic"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 agent heuristic does not match batch agent: random" in (
        captured.err
    )


def test_cli_replay_rejects_experiment_result_non_string_agent(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_experiment_result_agent_type.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["agent"] = ["random"]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 agent must be a string" in captured.err


def test_cli_replay_rejects_experiment_result_seed_mismatch(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_seed.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["seed"] = 6
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 seed 6 does not match expected seed: 5" in captured.err


def test_cli_replay_rejects_experiment_result_turns_above_max(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_turns.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["turns"] = 51
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 turns 51 exceeds max_turns: 50" in captured.err


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
