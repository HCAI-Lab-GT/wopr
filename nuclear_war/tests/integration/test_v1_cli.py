"""CLI tests for Nuclear War v1 commands."""

from __future__ import annotations

import json
import subprocess

from nuclear_war_env.cli import main


def test_cli_simulate_replay_and_summarize(tmp_path) -> None:
    output = tmp_path / "run.json"
    code = main(
        [
            "simulate",
            "--mode",
            "table",
            "--players",
            "2",
            "--seed",
            "3",
            "--agent",
            "heuristic",
            "--out",
            str(output),
        ]
    )
    assert code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["seed"] == 3
    assert payload["active_variant"]["variant_id"] == "base_later_two_d10"
    assert main(["replay", str(output)]) == 0
    assert main(["summarize", str(output)]) == 0


def test_cli_simulate_accepts_max_turns(tmp_path) -> None:
    output = tmp_path / "bounded_run.json"
    code = main(
        [
            "simulate",
            "--mode",
            "table",
            "--players",
            "2",
            "--seed",
            "3",
            "--agent",
            "heuristic",
            "--max-turns",
            "1",
            "--out",
            str(output),
        ]
    )
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert code == 0
    assert payload["turns"] == 1
    assert payload["termination_reason"] == "max_turns"
    assert payload["winner"] is None


def test_cli_validate_rules() -> None:
    assert main(["validate-rules"]) == 0


def test_console_script_simulates_replay_json(tmp_path) -> None:
    output = tmp_path / "console_run.json"
    result = subprocess.run(
        [
            "nuclear-war",
            "simulate",
            "--mode",
            "table",
            "--players",
            "2",
            "--seed",
            "3",
            "--agent",
            "heuristic",
            "--out",
            str(output),
        ],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["seed"] == 3
    assert payload["mode"] == "table"
    assert payload["active_variant"]["variant_id"] == "base_later_two_d10"


def test_cli_rejects_invalid_simulation_player_count(tmp_path, capsys) -> None:
    output = tmp_path / "run.json"
    code = main(
        [
            "simulate",
            "--mode",
            "table",
            "--players",
            "1",
            "--seed",
            "3",
            "--agent",
            "heuristic",
            "--out",
            str(output),
        ]
    )
    captured = capsys.readouterr()
    assert code == 2
    assert "At least two players are required" in captured.err
    assert not output.exists()


def test_cli_rejects_invalid_argparse_choice_without_raising(tmp_path, capsys) -> None:
    output = tmp_path / "run.json"
    code = main(
        [
            "simulate",
            "--mode",
            "space",
            "--players",
            "2",
            "--seed",
            "3",
            "--agent",
            "heuristic",
            "--out",
            str(output),
        ]
    )
    captured = capsys.readouterr()
    assert code == 2
    assert "invalid choice: 'space'" in captured.err
    assert not output.exists()
