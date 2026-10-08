"""CLI path validation tests for Nuclear War v1."""

from __future__ import annotations

from nuclear_war_env.cli import main


def test_cli_replay_rejects_directory_path(tmp_path, capsys) -> None:
    code = _main_without_raw_directory_error(["replay", str(tmp_path)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay path is not a file" in captured.err
    assert str(tmp_path) in captured.err


def test_cli_simulate_rejects_directory_output_path(tmp_path, capsys) -> None:
    code = _main_without_raw_directory_error(
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
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay path is a directory" in captured.err
    assert str(tmp_path) in captured.err


def test_cli_experiment_rejects_directory_output_path_before_batch(
    tmp_path, capsys, monkeypatch
) -> None:
    def fail_run_experiment(_config):
        raise AssertionError("experiment should not start for invalid output path")

    monkeypatch.setattr("nuclear_war_env.cli.run_experiment", fail_run_experiment)

    code = _main_without_raw_directory_error(
        [
            "experiment",
            "--mode",
            "table",
            "--players",
            "2",
            "--seed-start",
            "3",
            "--runs",
            "1",
            "--agent",
            "heuristic",
            "--out",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay path is a directory" in captured.err
    assert str(tmp_path) in captured.err


def test_cli_simulate_rejects_file_parent_output_path(tmp_path, capsys) -> None:
    parent_file = tmp_path / "not_a_directory"
    parent_file.write_text("occupied", encoding="utf-8")
    output = parent_file / "run.json"

    code = _main_without_raw_directory_error(
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

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay parent path is not a directory" in captured.err
    assert str(parent_file) in captured.err


def _main_without_raw_directory_error(args: list[str]) -> int:
    try:
        return main(args)
    except OSError:
        return -1
