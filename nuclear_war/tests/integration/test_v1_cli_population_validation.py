"""CLI population validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_negative_final_population(tmp_path, capsys) -> None:
    invalid = tmp_path / "negative_replay_population.json"
    payload = _replay_payload()
    payload["final_populations"]["player_0"] = -1
    payload["eliminations"] = ["player_0"]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay final_populations player_0 must be nonnegative" in captured.err


def test_cli_replay_rejects_negative_experiment_population(tmp_path, capsys) -> None:
    invalid = tmp_path / "negative_experiment_population.json"
    payload = _experiment_payload()
    payload["results"][0]["final_populations"]["player_0"] = -1
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 final_populations player_0 must be nonnegative"
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
        "actions": [],
        "events": [],
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
