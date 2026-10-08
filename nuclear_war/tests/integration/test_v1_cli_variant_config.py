"""CLI variant config plumbing tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main


def test_cli_simulate_accepts_active_variant_flag(tmp_path) -> None:
    output = tmp_path / "active_variant_run.json"

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
            "--variant",
            "base_later_two_d10",
            "--out",
            str(output),
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert code == 0
    assert payload["active_variant"]["variant_id"] == "base_later_two_d10"


def test_cli_simulate_rejects_deferred_variant_before_output(tmp_path, capsys) -> None:
    output = tmp_path / "deferred_variant_run.json"

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
            "--variant",
            "classic_spinner_scan",
            "--out",
            str(output),
        ]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "classic_spinner_scan is deferred" in captured.err
    assert "spinner probabilities" in captured.err
    assert not output.exists()


def test_cli_experiment_accepts_active_variant_flag(tmp_path) -> None:
    output = tmp_path / "active_variant_batch.json"

    code = main(
        [
            "experiment",
            "--mode",
            "table",
            "--players",
            "2",
            "--seed-start",
            "3",
            "--runs",
            "2",
            "--agent",
            "random",
            "--max-turns",
            "1",
            "--variant",
            "base_later_two_d10",
            "--out",
            str(output),
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert code == 0
    assert [
        result["active_variant"]["variant_id"] for result in payload["results"]
    ] == ["base_later_two_d10", "base_later_two_d10"]


def test_cli_experiment_rejects_deferred_variant_before_output(
    tmp_path,
    capsys,
) -> None:
    output = tmp_path / "deferred_variant_batch.json"

    code = main(
        [
            "experiment",
            "--mode",
            "table",
            "--players",
            "2",
            "--seed-start",
            "3",
            "--runs",
            "2",
            "--agent",
            "random",
            "--max-turns",
            "1",
            "--variant",
            "classic_spinner_scan",
            "--out",
            str(output),
        ]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "classic_spinner_scan is deferred" in captured.err
    assert "spinner probabilities" in captured.err
    assert not output.exists()
