"""Phase 0 PettingZoo AEC stub environment."""

from __future__ import annotations

from numbers import Integral
from typing import Any

import numpy as np
from gymnasium import spaces
from pettingzoo import AECEnv
from pettingzoo.utils import AgentSelector


class Phase0AECEnv(AECEnv):
    """Minimal deterministic environment to satisfy PettingZoo api_test."""

    metadata = {"name": "nuclear_war_phase0_aec_stub_v0"}

    def __init__(self, seed: int | None = None, max_cycles: int = 2) -> None:
        super().__init__()
        self.possible_agents = ["player_0", "player_1"]
        self._seed = seed
        self._rng = np.random.default_rng(seed)
        self.max_cycles = max_cycles
        self.action_spaces = {
            agent: spaces.Discrete(2) for agent in self.possible_agents
        }
        self.observation_spaces = {
            agent: spaces.Dict(
                {
                    "observation": spaces.Box(
                        low=0.0,
                        high=1.0,
                        shape=(1,),
                        dtype=np.float32,
                    ),
                    "action_mask": spaces.Box(
                        low=0,
                        high=1,
                        shape=(2,),
                        dtype=np.int8,
                    ),
                }
            )
            for agent in self.possible_agents
        }
        self.reset(seed=seed)

    def reset(
        self,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> None:
        self.agents = list(self.possible_agents)
        self.rewards = {agent: 0.0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0.0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self._cycle_count = 0
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self._agent_selector = AgentSelector(self.agents)
        self.agent_selection = self._agent_selector.next()
        self._last_actions = {agent: 0 for agent in self.agents}
        self._observations = {
            agent: np.zeros(1, dtype=np.float32) for agent in self.agents
        }

    def step(self, action: int | None) -> None:
        agent = self.agent_selection
        self._clear_rewards()
        if self.terminations[agent] or self.truncations[agent]:
            self._was_dead_step(action)
            return
        self._last_actions[agent] = _action_value(action)
        self._observations[agent] = np.array(
            [self._last_actions[agent]],
            dtype=np.float32,
        )
        self.rewards[agent] = 0.0
        if agent == self.possible_agents[-1]:
            self._cycle_count += 1
            if self._cycle_count >= self.max_cycles:
                for live_agent in self.agents:
                    self.truncations[live_agent] = True
        self.agent_selection = self._agent_selector.next()
        self._accumulate_rewards()

    def observe(self, agent: str) -> dict[str, np.ndarray]:
        mask = np.ones(2, dtype=np.int8)
        if self.truncations.get(agent, False) or self.terminations.get(agent, False):
            mask = np.zeros(2, dtype=np.int8)
        return {
            "observation": self._observations.get(agent, np.zeros(1, dtype=np.float32)),
            "action_mask": mask,
        }

    def render(self) -> str:
        return (
            f"Phase0AECEnv cycle={self._cycle_count} last_actions={self._last_actions}"
        )

    def close(self) -> None:
        return


__all__ = ["Phase0AECEnv"]


def _action_value(action: int | None) -> int:
    if action is None:
        return 0
    if isinstance(action, bool) or not isinstance(action, Integral):
        raise ValueError("Action must be an integer")
    return int(action)
