"""CLI experiment summary field validation tests for Nuclear War v1."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_experiment_summary_extra_field(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_summary_extra_field.json"
    payload = _valid_experiment_payload()
    payload["summary"]["unexpected"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Experiment summary fields are invalid" in captured.err


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
