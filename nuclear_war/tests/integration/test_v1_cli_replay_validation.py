"""CLI replay validation tests for Nuclear War v1."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_missing_file(tmp_path, capsys) -> None:
    missing = tmp_path / "missing.json"
    code = main(["replay", str(missing)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay file not found" in captured.err
    assert str(missing) in captured.err


def test_cli_replay_rejects_malformed_json(tmp_path, capsys) -> None:
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{not json", encoding="utf-8")
    code = main(["replay", str(malformed)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay file is not valid JSON" in captured.err
    assert str(malformed) in captured.err


def test_cli_summarize_rejects_invalid_replay_schema(tmp_path, capsys) -> None:
    invalid = tmp_path / "not_replay.json"
    invalid.write_text(json.dumps({"mode": "table"}), encoding="utf-8")
    code = main(["summarize", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay file missing required field: seed" in captured.err


def test_cli_replay_rejects_invalid_replay_schema(tmp_path, capsys) -> None:
    invalid = tmp_path / "not_replay.json"
    invalid.write_text(json.dumps({"mode": "table"}), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay file missing required field: seed" in captured.err


def test_cli_replay_rejects_non_object_json(tmp_path, capsys) -> None:
    invalid = tmp_path / "not_object.json"
    invalid.write_text(json.dumps(7), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay payload must be an object" in captured.err


def test_cli_replay_rejects_missing_action_log(tmp_path, capsys) -> None:
    invalid = tmp_path / "summary_only.json"
    invalid.write_text(json.dumps(_summary_only_payload()), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay file missing required field: actions" in captured.err


def test_cli_replay_rejects_incomplete_action_log_entry(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_entry.json"
    payload = _summary_only_payload()
    payload["actions"] = [{"turn": 1}]
    payload["events"] = []
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 missing required field: player_id" in captured.err


def test_cli_replay_rejects_incomplete_experiment_result(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment.json"
    invalid.write_text(json.dumps(_bad_experiment_payload()), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 missing required field: final_populations" in captured.err
    )


def test_cli_replay_rejects_incomplete_experiment_summary(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_experiment_summary.json"
    payload = _bad_experiment_payload()
    payload["results"][0]["final_populations"] = {"player_0": 0, "player_1": 30}
    payload["summary"] = {
        "termination_counts": {"one_player_remaining": 1},
        "winner_counts": {"player_1": 1},
        "average_turns": 20.0,
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment summary missing required field: total_eliminations" in captured.err
    )


def _summary_only_payload() -> dict:
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
    }


def _bad_experiment_payload() -> dict:
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
                "termination_reason": "one_player_remaining",
            }
        ],
        "summary": {},
    }
