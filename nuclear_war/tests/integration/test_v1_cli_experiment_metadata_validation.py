"""CLI experiment batch metadata validation tests for Nuclear War v1."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_experiment_with_invalid_batch_mode(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_batch_mode.json"
    payload = _valid_experiment_payload()
    payload["mode"] = "classic"
    payload["results"][0]["mode"] = "classic"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment has invalid mode: classic" in captured.err


def test_cli_replay_rejects_experiment_with_invalid_batch_agent(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_batch_agent.json"
    payload = _valid_experiment_payload()
    payload["agent"] = "passive"
    payload["results"][0]["agent"] = "passive"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment has invalid agent: passive" in captured.err


def test_cli_replay_rejects_experiment_with_invalid_batch_players(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_batch_players.json"
    payload = _valid_experiment_payload()
    payload["players"] = 1
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment has invalid players: 1" in captured.err


def test_cli_replay_rejects_experiment_with_press_enabled(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_batch_press.json"
    payload = _valid_experiment_payload()
    payload["press"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment press must be false for v1" in captured.err


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
