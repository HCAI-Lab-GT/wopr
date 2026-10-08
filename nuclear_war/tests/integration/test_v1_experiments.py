"""Experiment runner tests for Nuclear War v1."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nuclear_war_env.cli import main
from nuclear_war_env.experiments import ExperimentConfig, run_experiment


def test_experiment_runner_is_reproducible() -> None:
    config = ExperimentConfig(
        mode="postal",
        players=3,
        seed_start=20,
        runs=3,
        agent="heuristic",
        max_turns=5,
    )
    first = run_experiment(config)
    second = run_experiment(config)
    assert first == second
    assert first["runs"] == 3
    assert len(first["results"]) == 3
    assert first["results"][0]["active_variant"]["variant_id"] == "base_later_two_d10"
    assert first["summary"]["termination_counts"]


def test_experiment_runner_rejects_press_mode_before_simulation(monkeypatch) -> None:
    def fail_run_simulation(_config):
        raise AssertionError("simulation should not start for press mode")

    monkeypatch.setattr(
        "nuclear_war_env.experiments.run_simulation", fail_run_simulation
    )
    config = ExperimentConfig(
        mode="postal",
        players=3,
        seed_start=20,
        runs=3,
        agent="heuristic",
        max_turns=5,
        press=True,
    )
    with pytest.raises(ValueError, match="Postal press is deferred"):
        run_experiment(config)


def test_cli_experiment_writes_batch_output(tmp_path) -> None:
    output = tmp_path / "experiment.json"
    code = main(
        [
            "experiment",
            "--mode",
            "table",
            "--players",
            "2",
            "--seed-start",
            "5",
            "--runs",
            "2",
            "--agent",
            "random",
            "--out",
            str(output),
        ]
    )
    assert code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["mode"] == "table"
    assert payload["agent"] == "random"
    assert [run["seed"] for run in payload["results"]] == [5, 6]
    assert main(["replay", str(output)]) == 0
    assert main(["summarize", str(output)]) == 0


def test_v1_acceptance_doc_tracks_rule_fidelity() -> None:
    path = Path("docs/v1_acceptance.md")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "Rule Fidelity" in text
    assert "no-press" in text
    assert "validate-source-evidence" in text
    assert "card_effect_evidence_coverage" in text
    assert "card_effect_evidence_promotion_errors" in text
    assert "second-pass verified" in text.lower()
    assert "external social-simulation frameworks" in text.lower()
