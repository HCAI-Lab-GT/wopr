"""CLI experiment result row validation tests for Nuclear War v1."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_experiment_result_without_variant_object(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_result_variant.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["active_variant"] = "base_later_two_d10"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 active_variant must be an object" in captured.err


def test_cli_replay_rejects_experiment_result_without_elimination_list(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_result_eliminations.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["eliminations"] = "player_0"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 eliminations must be a list" in captured.err


def test_cli_replay_rejects_experiment_result_without_string_elimination(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_result_elimination_value.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["eliminations"] = [7]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 elimination 0 must be a string" in captured.err


def test_cli_replay_rejects_experiment_result_without_population_object(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_result_populations.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["final_populations"] = [["player_0", 0]]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 final_populations must be an object" in captured.err


def test_cli_replay_rejects_experiment_result_without_integer_population(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_result_population_value.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["final_populations"]["player_0"] = "0"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 final_populations player_0 must be an integer"
        in captured.err
    )


def test_cli_replay_rejects_experiment_result_without_string_or_null_winner(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_result_winner.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["winner"] = 7
    payload["summary"]["winner_counts"] = {"7": 1}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 winner must be a string or null" in captured.err


def test_cli_replay_rejects_experiment_result_without_termination_string(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_result_termination.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["termination_reason"] = None
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 termination_reason must be a string" in captured.err


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
