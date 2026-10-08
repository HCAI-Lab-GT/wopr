"""Simulation winner semantics tests."""

from __future__ import annotations

from nuclear_war_env.simulation import SimulationConfig, run_simulation


def test_simulation_does_not_name_winner_on_multi_survivor_max_turns() -> None:
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=3,
        agent="heuristic",
        max_turns=1,
    )

    result = run_simulation(config)

    assert result["termination_reason"] == "max_turns"
    assert sum(1 for value in result["final_populations"].values() if value > 0) > 1
    assert result["winner"] is None
