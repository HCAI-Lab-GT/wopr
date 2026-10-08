"""The heuristic agent should be measurably better than random at landing attacks."""

from __future__ import annotations

from collections import Counter

from nuclear_war_env.simulation import SimulationConfig, run_simulation


def _warhead_load_rate(agent: str) -> float:
    loaded = 0
    attempted = 0
    for seed in range(1, 25):
        config = SimulationConfig(
            mode="table", players=3, seed=seed, agent=agent, max_turns=60
        )
        result = run_simulation(config)
        counts = Counter(event["event_type"] for event in result["events"])
        loaded += counts.get("warhead_loaded", 0)
        attempted += counts.get("warhead_loaded", 0) + counts.get(
            "warhead_discarded", 0
        )
    return loaded / attempted if attempted else 0.0


def test_heuristic_lands_warheads_more_reliably_than_random() -> None:
    # The heuristic builds delivery->warhead launches; random places blindly and
    # wastes far more warheads. The heuristic's load rate should clearly exceed it.
    assert _warhead_load_rate("heuristic") > _warhead_load_rate("random") + 0.1
