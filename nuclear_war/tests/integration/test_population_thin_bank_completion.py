"""5-6 player table games complete despite the thin population bank.

The 5-6 player deal consumes 35-36 of the 40 population cards, so the bank
cannot always make exact change. These seeds crashed with
"Cannot make population total" before the round-down fallback in
``rebalance_population_cards`` (sweep of seeds 1-80, heuristic, max_turns=100).
"""

from __future__ import annotations

import pytest

from nuclear_war_env.simulation import SimulationConfig, run_simulation

FIVE_PLAYER_CRASH_SEEDS = (9, 23, 60, 65, 73)
SIX_PLAYER_CRASH_SEEDS = (1, 7, 15, 28, 30, 32, 33, 34, 45, 53, 57, 60, 65, 71, 76)


def _run(players: int, seed: int) -> tuple:
    result = run_simulation(
        SimulationConfig(
            mode="table",
            players=players,
            seed=seed,
            agent="heuristic",
            max_turns=100,
        )
    )
    assert result["players"] == players
    assert result["termination_reason"]
    assert all(value >= 0 for value in result["final_populations"].values())
    return (
        result["winner"],
        result["termination_reason"],
        tuple(sorted(result["final_populations"].items())),
    )


@pytest.mark.parametrize("seed", FIVE_PLAYER_CRASH_SEEDS)
def test_five_player_thin_bank_seed_completes(seed: int) -> None:
    _run(5, seed)


@pytest.mark.parametrize("seed", SIX_PLAYER_CRASH_SEEDS)
def test_six_player_thin_bank_seed_completes(seed: int) -> None:
    _run(6, seed)


def test_thin_bank_fallback_outcomes_are_deterministic() -> None:
    assert _run(6, SIX_PLAYER_CRASH_SEEDS[0]) == _run(6, SIX_PLAYER_CRASH_SEEDS[0])
