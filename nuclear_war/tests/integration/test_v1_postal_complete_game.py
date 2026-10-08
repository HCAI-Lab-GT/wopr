"""Postal complete-game simulation tests."""

from __future__ import annotations

from nuclear_war_env.simulation import SimulationConfig, run_simulation


def test_postal_simulation_can_end_with_one_player_remaining() -> None:
    config = SimulationConfig(
        mode="postal",
        players=3,
        seed=2,
        agent="heuristic",
        max_turns=80,
    )

    result = run_simulation(config)

    assert result["termination_reason"] == "one_player_remaining"
    # Exactly one survivor with positive population; everyone else eliminated.
    # Assert the invariant, not a seed-fragile winner id / population.
    survivors = [
        player_id
        for player_id, population in result["final_populations"].items()
        if population > 0
    ]
    assert survivors == [result["winner"]]
    assert result["winner"] is not None
    assert all(
        population == 0
        for player_id, population in result["final_populations"].items()
        if player_id != result["winner"]
    )
