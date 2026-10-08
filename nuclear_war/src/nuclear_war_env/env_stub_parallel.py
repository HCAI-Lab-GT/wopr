"""Phase 0 PettingZoo parallel stub environment."""

from __future__ import annotations

from numbers import Integral
from typing import Any

import numpy as np
from gymnasium import spaces
from pettingzoo import ParallelEnv


class Phase0ParallelEnv(ParallelEnv):
    """Minimal deterministic parallel environment for compliance tests."""

    metadata = {"name": "nuclear_war_phase0_parallel_stub_v0"}

    def __init__(self, seed: int | None = None, max_cycles: int = 2) -> None:
        self.possible_agents = ["player_0", "player_1"]
        self._seed = seed
        self._rng = np.random.default_rng(seed)
        self.max_cycles = max_cycles
        self._cycle_count = 0
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

    def reset(
        self,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[dict[str, dict[str, np.ndarray]], dict[str, dict[str, Any]]]:
        if seed is not None:
            self._rng = np.random.default_rng(seed)
        self._cycle_count = 0
        self.agents = list(self.possible_agents)
        observations = {
            agent: {
                "observation": np.zeros(1, dtype=np.float32),
                "action_mask": np.ones(2, dtype=np.int8),
            }
            for agent in self.possible_agents
        }
        infos = {agent: {} for agent in self.possible_agents}
        return observations, infos

    def step(
        self, action_dict: dict[str, int]
    ) -> tuple[
        dict[str, dict[str, np.ndarray]],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict[str, Any]],
    ]:
        self._cycle_count += 1
        rewards = {agent: 0.0 for agent in self.possible_agents}
        terminations = {agent: False for agent in self.possible_agents}
        truncations = {
            agent: self._cycle_count >= self.max_cycles
            for agent in self.possible_agents
        }
        infos = {
            agent: {"last_action": _action_value(action_dict.get(agent))}
            for agent in self.possible_agents
        }
        observations = {
            agent: {
                "observation": np.array(
                    [infos[agent]["last_action"]],
                    dtype=np.float32,
                ),
                "action_mask": (
                    np.zeros(2, dtype=np.int8)
                    if truncations[agent] or terminations[agent]
                    else np.ones(2, dtype=np.int8)
                ),
            }
            for agent in self.possible_agents
        }
        if all(truncations.values()):
            observations = {}
            self.agents = []
        else:
            self.agents = list(self.possible_agents)
        return observations, rewards, terminations, truncations, infos

    def render(self) -> str:
        return f"Phase0ParallelEnv cycle={self._cycle_count}"

    def close(self) -> None:
        return


__all__ = ["Phase0ParallelEnv"]


def _action_value(action: int | None) -> int:
    if action is None:
        return 0
    if isinstance(action, bool) or not isinstance(action, Integral):
        raise ValueError("Action must be an integer")
    return int(action)
