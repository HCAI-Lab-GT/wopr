"""PettingZoo Parallel environment for postal no-press Nuclear War."""

from __future__ import annotations

from typing import Any

from pettingzoo import ParallelEnv

from .actions import apply_action, legal_actions
from .engine import execute_postal_turn
from .engine.terminal import game_over, player_final_strike_pending
from .env_config_validation import validate_max_cycles
from .env_rewards import terminal_reward
from .env_utils import action_space, env_observation, observation_space, select_action
from .players import player_ids
from .press import reject_press_mode
from .rng import validate_seed
from .setup_game import create_game_state


class PostalParallelEnv(ParallelEnv):
    """Simultaneous postal no-press environment backed by the deterministic engine.

    Step returns are keyed on the agents that acted this step, each receiving
    its (possibly final) observation. Terminal rewards follow ``env_rewards``.
    """

    metadata = {"name": "nuclear_war_postal_v1"}

    def __init__(
        self,
        seed: int | None = None,
        press: bool = False,
        max_cycles: int = 50,
        players: int = 2,
    ) -> None:
        reject_press_mode(press)
        self.possible_agents = player_ids(players)
        validate_seed(seed)
        self._seed = seed
        self.press = press
        self.max_cycles = validate_max_cycles(max_cycles)
        self.action_spaces = {agent: action_space() for agent in self.possible_agents}
        self.observation_spaces = {
            agent: observation_space() for agent in self.possible_agents
        }
        self._cycle_count = 0
        self._has_reset = False

    def reset(
        self,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[dict[str, dict], dict[str, dict[str, Any]]]:
        resolved_seed = self._seed if seed is None else seed
        self.game_state = create_game_state(
            "postal", len(self.possible_agents), resolved_seed, press=self.press
        )
        self.agents = list(self.possible_agents)
        self._cycle_count = 0
        self._has_reset = True
        return self._observations(), {agent: {} for agent in self.agents}

    def step(
        self,
        action_dict: dict[str, object],
    ) -> tuple[
        dict[str, dict],
        dict[str, float],
        dict[str, bool],
        dict[str, bool],
        dict[str, dict[str, Any]],
    ]:
        infos: dict[str, dict[str, Any]] = {}
        if not self._has_reset:
            raise ValueError("Environment must be reset before stepping")
        if not self.agents:
            raise ValueError("Cannot step after environment has ended")
        if not isinstance(action_dict, dict):
            raise ValueError("Parallel actions must be a dictionary")
        live_agents = set(self.agents)
        for agent in action_dict:
            if agent not in live_agents:
                raise ValueError(f"Unknown action agent: {agent}")
        available_actions = {
            agent: legal_actions(self.game_state, agent, "postal")
            for agent in self.agents
        }
        for agent in list(self.agents):
            actions = available_actions[agent]
            if agent not in action_dict:
                raise ValueError(f"Missing action for live agent {agent}")
            action = action_dict[agent]
            if action is None:
                raise ValueError(f"Missing action for live agent {agent}")
            selected = select_action(actions, action)
            events = apply_action(self.game_state, selected)
            infos[agent] = {"events": [event.event_type for event in events]}
        postal_events = execute_postal_turn(self.game_state)
        for agent in self.agents:
            infos.setdefault(agent, {})["postal_events"] = [
                event.event_type for event in postal_events
            ]
        self._cycle_count += 1
        self.game_state.turn = self._cycle_count
        done = game_over(self.game_state)
        truncated = self._cycle_count >= self.max_cycles
        active_agents = [] if done else self._active_agents()
        acted = list(self.agents)
        rewards: dict[str, float] = {}
        terminations: dict[str, bool] = {}
        truncations: dict[str, bool] = {}
        for agent in acted:
            terminated = done or agent not in active_agents
            terminations[agent] = terminated
            truncations[agent] = truncated
            rewards[agent] = (
                terminal_reward(self.game_state.players[agent], done)
                if terminated
                else 0.0
            )
        observations = self._observations(acted)
        self.agents = [] if truncated else active_agents
        return observations, rewards, terminations, truncations, infos

    def render(self) -> str:
        return f"PostalParallelEnv cycle={self._cycle_count}"

    def action_space(self, agent: str) -> Any:
        return self.action_spaces[agent]

    def observation_space(self, agent: str) -> Any:
        return self.observation_spaces[agent]

    def _observations(self, agents: list[str] | None = None) -> dict[str, dict]:
        return {
            agent: env_observation(self.game_state, agent, "postal")
            for agent in (self.agents if agents is None else agents)
        }

    def _active_agents(self) -> list[str]:
        return [
            agent
            for agent in self.possible_agents
            if self.game_state.players[agent].alive
            or player_final_strike_pending(self.game_state.players[agent])
        ]


__all__ = ["PostalParallelEnv"]
