"""Runtime variant config validation tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.experiments import ExperimentConfig, run_experiment
from nuclear_war_env.simulation import SimulationConfig, run_simulation


def test_simulation_rejects_deferred_variant_before_loading_rules(monkeypatch) -> None:
    def fail_load_rules(_path):
        raise AssertionError("rules should not load for deferred variant")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=3,
        agent="random",
        max_turns=1,
        variant_id="classic_spinner_scan",
    )

    with pytest.raises(ValueError, match="classic_spinner_scan is deferred"):
        run_simulation(config)


def test_experiment_rejects_deferred_variant_before_simulation(monkeypatch) -> None:
    def fail_run_simulation(_config):
        raise AssertionError("simulation should not start for deferred variant")

    monkeypatch.setattr(
        "nuclear_war_env.experiments.run_simulation", fail_run_simulation
    )
    config = ExperimentConfig(
        mode="table",
        players=2,
        seed_start=3,
        runs=1,
        agent="random",
        max_turns=1,
        variant_id="classic_spinner_scan",
    )

    with pytest.raises(ValueError, match="classic_spinner_scan is deferred"):
        run_experiment(config)
