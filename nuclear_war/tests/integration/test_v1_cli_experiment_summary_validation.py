"""CLI experiment summary validation tests for Nuclear War v1."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_experiment_termination_summary_mismatch(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_termination_summary.json"
    payload = _valid_experiment_payload()
    payload["summary"]["termination_counts"] = {"max_turns": 1}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment summary termination_counts does not match results" in captured.err
    )


def test_cli_replay_rejects_experiment_winner_summary_mismatch(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_winner_summary.json"
    payload = _valid_experiment_payload()
    payload["summary"]["winner_counts"] = {"no_winner": 1}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment summary winner_counts does not match results" in captured.err


def test_cli_replay_rejects_experiment_average_turns_mismatch(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_average_turns.json"
    payload = _valid_experiment_payload()
    payload["summary"]["average_turns"] = 21.0
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment summary average_turns does not match results" in captured.err


def test_cli_replay_rejects_experiment_elimination_summary_mismatch(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_eliminations_summary.json"
    payload = _valid_experiment_payload()
    payload["summary"]["total_eliminations"] = 0
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment summary total_eliminations does not match results" in captured.err
    )


def test_cli_replay_rejects_boolean_summary_count(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_boolean_summary_count.json"
    payload = _valid_experiment_payload()
    payload["summary"]["termination_counts"] = {"one_player_remaining": True}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment summary termination_counts values must be integers" in captured.err
    )


def test_cli_replay_rejects_negative_summary_count(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_negative_summary_count.json"
    payload = _valid_experiment_payload()
    payload["summary"]["termination_counts"] = {"one_player_remaining": -1}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment summary termination_counts values must be nonnegative"
        in captured.err
    )


def test_cli_replay_rejects_boolean_total_eliminations(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_boolean_total_eliminations.json"
    payload = _valid_experiment_payload()
    payload["summary"]["total_eliminations"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment summary total_eliminations must be an integer" in captured.err


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
