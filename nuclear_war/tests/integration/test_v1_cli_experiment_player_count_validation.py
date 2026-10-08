"""CLI experiment player-count consistency validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_experiment_population_count_mismatch(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_experiment_population_count.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["final_populations"] = {"player_0": 0}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 final_populations count 1 does not match players: 2"
        in captured.err
    )


def test_cli_replay_rejects_experiment_population_id_mismatch(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_population_ids.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["final_populations"] = {"player_0": 0, "rogue": 30}
    payload["results"][0]["eliminations"] = []
    payload["summary"]["total_eliminations"] = 0
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 final_populations keys must match players" in captured.err
    )


def test_cli_replay_rejects_experiment_unknown_winner(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_winner.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["winner"] = "rogue"
    payload["summary"]["winner_counts"] = {"rogue": 1}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 winner must be a known player id or null" in captured.err
    )


def test_cli_replay_rejects_experiment_winner_that_contradicts_populations(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_experiment_winner_population.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["winner"] = "player_0"
    payload["summary"]["winner_counts"] = {"player_0": 1}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 winner does not match final populations" in captured.err


def test_cli_replay_rejects_experiment_unknown_elimination(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_elimination.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["eliminations"] = ["rogue"]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment result 0 elimination 0 must be a known player id" in captured.err


def test_cli_replay_rejects_experiment_eliminations_that_contradict_populations(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_experiment_elimination_population.json"
    payload = _valid_experiment_payload()
    payload["results"][0]["eliminations"] = []
    payload["summary"]["total_eliminations"] = 0
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 eliminations do not match final populations"
        in captured.err
    )


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
