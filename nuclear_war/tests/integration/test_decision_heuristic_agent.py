"""Decision heuristic public wiring tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_env.cli import main
from nuclear_war_env.experiments import ExperimentConfig, run_experiment
from nuclear_war_env.simulation import SimulationConfig, run_simulation

AGENT = "decision_heuristic"


def test_table_simulation_accepts_decision_heuristic() -> None:
    result = run_simulation(
        SimulationConfig(
            mode="table",
            players=3,
            seed=1,
            agent=AGENT,
            max_turns=3,
        )
    )

    assert result["agent"] == AGENT


def test_postal_simulation_rejects_decision_heuristic() -> None:
    with pytest.raises(ValueError, match="decision_heuristic is table-only"):
        run_simulation(
            SimulationConfig(
                mode="postal",
                players=3,
                seed=1,
                agent=AGENT,
                max_turns=3,
            )
        )


def test_table_experiment_accepts_decision_heuristic() -> None:
    result = run_experiment(
        ExperimentConfig(
            mode="table",
            players=3,
            seed_start=1,
            runs=1,
            agent=AGENT,
            max_turns=3,
        )
    )

    assert result["agent"] == AGENT
    assert result["results"][0]["agent"] == AGENT


def test_postal_experiment_rejects_decision_heuristic() -> None:
    with pytest.raises(ValueError, match="decision_heuristic is table-only"):
        run_experiment(
            ExperimentConfig(
                mode="postal",
                players=3,
                seed_start=1,
                runs=1,
                agent=AGENT,
                max_turns=3,
            )
        )


def test_cli_simulate_and_replay_accept_decision_heuristic(tmp_path) -> None:
    output = tmp_path / "decision_heuristic.json"

    code = main(
        [
            "simulate",
            "--mode",
            "table",
            "--players",
            "3",
            "--seed",
            "1",
            "--agent",
            AGENT,
            "--max-turns",
            "3",
            "--out",
            str(output),
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert code == 0
    assert payload["agent"] == AGENT
    assert main(["replay", str(output)]) == 0


def test_cli_experiment_and_replay_accept_decision_heuristic(tmp_path) -> None:
    output = tmp_path / "decision_heuristic_batch.json"

    code = main(
        [
            "experiment",
            "--mode",
            "table",
            "--players",
            "3",
            "--seed-start",
            "1",
            "--runs",
            "1",
            "--agent",
            AGENT,
            "--max-turns",
            "3",
            "--out",
            str(output),
        ]
    )

    payload = json.loads(output.read_text(encoding="utf-8"))
    assert code == 0
    assert payload["agent"] == AGENT
    assert main(["replay", str(output)]) == 0
