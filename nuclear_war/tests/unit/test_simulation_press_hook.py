"""Simulation press_hook seam tests."""

from __future__ import annotations

from nuclear_war_env.agent_protocol import DecisionAgent
from nuclear_war_env.simulation import (
    SimulationConfig,
    run_table_simulation_with_decision_agents,
)


class _FirstLegalAgent(DecisionAgent):
    def choose(self, observation, options):
        return options[0]


def test_press_hook_called_once_per_round_when_set() -> None:
    calls: list[int] = []

    def hook(state, completed_round: int) -> None:
        calls.append(completed_round)

    agents = {
        pid: _FirstLegalAgent()
        for pid in ["player_0", "player_1", "player_2", "player_3"]
    }
    config = SimulationConfig(
        mode="table",
        players=4,
        seed=81,
        agent="decision_heuristic",
        max_turns=2,
        press=False,
    )

    run_table_simulation_with_decision_agents(config, agents, press_hook=hook)

    assert calls == [1]


def test_press_hook_absent_preserves_default_path() -> None:
    agents = {
        pid: _FirstLegalAgent()
        for pid in ["player_0", "player_1", "player_2", "player_3"]
    }
    config = SimulationConfig(
        mode="table",
        players=4,
        seed=81,
        agent="decision_heuristic",
        max_turns=1,
        press=False,
    )

    replay = run_table_simulation_with_decision_agents(config, agents)

    assert replay["mode"] == "table"
    assert replay["turns"] >= 1
