"""Smoke test for the parity sweep runner.

Runs a small slice of the documented parity grid and asserts the parity
invariant: a second pass over the same grid is identical to the first.
The full 240-game grid is reproducible on demand via
`nuclear_war/scripts/run_parity_sweep.py`.
"""

from __future__ import annotations

from nuclear_war_env.simulation import SimulationConfig, run_simulation


def _outcome(agent: str, seed: int) -> tuple[object, str, tuple[tuple[str, int], ...]]:
    result = run_simulation(SimulationConfig("table", 3, seed, agent, max_turns=80))
    standings = tuple(result["final_populations"].items())
    return (result["winner"], result["termination_reason"], standings)


def test_heuristic_slice_is_deterministic() -> None:
    for seed in range(1, 4):
        assert _outcome("heuristic", seed) == _outcome("heuristic", seed)


def test_random_slice_is_deterministic() -> None:
    for seed in range(1, 4):
        assert _outcome("random", seed) == _outcome("random", seed)
