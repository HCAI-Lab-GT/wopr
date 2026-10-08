"""Runtime string config validation tests for v1 public helpers."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_env.experiments import ExperimentConfig, run_experiment
from nuclear_war_env.simulation import SimulationConfig, run_simulation


def test_simulation_rejects_non_string_mode_before_loading_rules(monkeypatch) -> None:
    malformed_mode: Any = []

    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    config = SimulationConfig(
        mode=malformed_mode,
        players=2,
        seed=3,
        agent="random",
        max_turns=1,
    )

    with pytest.raises(ValueError, match="Simulation mode must be a string"):
        run_simulation(config)


def test_simulation_rejects_non_string_agent_before_loading_rules(monkeypatch) -> None:
    malformed_agent: Any = []

    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=3,
        agent=malformed_agent,
        max_turns=1,
    )

    with pytest.raises(ValueError, match="Simulation agent must be a string"):
        run_simulation(config)


def test_experiment_rejects_non_string_mode_before_simulation(monkeypatch) -> None:
    malformed_mode: Any = []

    def fail_run_simulation(_config):
        raise AssertionError("simulation should not start for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.experiments.run_simulation", fail_run_simulation
    )
    config = ExperimentConfig(
        mode=malformed_mode,
        players=2,
        seed_start=3,
        runs=1,
        agent="random",
        max_turns=1,
    )

    with pytest.raises(ValueError, match="Experiment mode must be a string"):
        run_experiment(config)


def test_experiment_rejects_non_string_agent_before_simulation(monkeypatch) -> None:
    malformed_agent: Any = []

    def fail_run_simulation(_config):
        raise AssertionError("simulation should not start for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.experiments.run_simulation", fail_run_simulation
    )
    config = ExperimentConfig(
        mode="table",
        players=2,
        seed_start=3,
        runs=1,
        agent=malformed_agent,
        max_turns=1,
    )

    with pytest.raises(ValueError, match="Experiment agent must be a string"):
        run_experiment(config)
