"""Runtime config validation tests for v1 public helpers."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_env.agent_names import REPLAY_AGENT_NAMES
from nuclear_war_env.experiments import ExperimentConfig, run_experiment
from nuclear_war_env.simulation import SimulationConfig, run_simulation
from nuclear_war_env.simulation_config_validation import validate_simulation_config
from nuclear_war_env.variants import ACTIVE_VARIANT_ID


def test_validate_simulation_config_rejects_mixed_seats_for_single_agent() -> None:
    # "mixed_seats" is a per-seat replay label, not a runnable single agent, so the
    # single-agent validator (its strict default) must reject it upfront.
    with pytest.raises(ValueError, match="Unknown agent: mixed_seats"):
        validate_simulation_config(
            "table", 2, 1, "mixed_seats", 1, False, ACTIVE_VARIANT_ID
        )


def test_validate_simulation_config_accepts_mixed_seats_for_decision_agents() -> None:
    # The per-seat (decision-agent) path opts into the replay label set, where
    # "mixed_seats" is a legitimate label.
    validate_simulation_config(
        "table",
        2,
        1,
        "mixed_seats",
        1,
        False,
        ACTIVE_VARIANT_ID,
        allowed_agents=REPLAY_AGENT_NAMES,
    )


def test_simulation_rejects_boolean_seed_before_loading_rules(monkeypatch) -> None:
    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=True,
        agent="random",
        max_turns=1,
    )

    with pytest.raises(ValueError, match="Simulation seed must be an integer"):
        run_simulation(config)


def test_simulation_rejects_boolean_max_turns_before_loading_rules(monkeypatch) -> None:
    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=3,
        agent="random",
        max_turns=True,
    )

    with pytest.raises(ValueError, match="Simulation max_turns must be an integer"):
        run_simulation(config)


def test_simulation_rejects_non_boolean_press_before_loading_rules(monkeypatch) -> None:
    malformed_press: Any = 0

    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=3,
        agent="random",
        max_turns=1,
        press=malformed_press,
    )

    with pytest.raises(ValueError, match="Press must be false for v1"):
        run_simulation(config)


def test_experiment_rejects_boolean_seed_start_before_simulation(monkeypatch) -> None:
    def fail_run_simulation(_config):
        raise AssertionError("simulation should not start for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.experiments.run_simulation", fail_run_simulation
    )
    config = ExperimentConfig(
        mode="table",
        players=2,
        seed_start=True,
        runs=1,
        agent="random",
        max_turns=1,
    )

    with pytest.raises(ValueError, match="Experiment seed_start must be an integer"):
        run_experiment(config)


def test_experiment_rejects_boolean_runs_before_simulation(monkeypatch) -> None:
    def fail_run_simulation(_config):
        raise AssertionError("simulation should not start for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.experiments.run_simulation", fail_run_simulation
    )
    config = ExperimentConfig(
        mode="table",
        players=2,
        seed_start=3,
        runs=True,
        agent="random",
        max_turns=1,
    )

    with pytest.raises(ValueError, match="Experiment runs must be an integer"):
        run_experiment(config)


def test_experiment_rejects_non_boolean_press_before_simulation(monkeypatch) -> None:
    malformed_press: Any = 0

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
        agent="random",
        max_turns=1,
        press=malformed_press,
    )

    with pytest.raises(ValueError, match="Press must be false for v1"):
        run_experiment(config)
