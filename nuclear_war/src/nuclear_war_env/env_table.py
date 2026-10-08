"""PettingZoo AEC environment for table-mode Nuclear War."""

from __future__ import annotations

from typing import Any

import numpy as np
from pettingzoo import AECEnv
from pettingzoo.utils import AgentSelector

from .action_models import LegalAction
from .decision_loop import apply_decision_result, pending_decision, start_game
from .engine.terminal import game_over, player_final_strike_pending
from .env_config_validation import validate_max_cycles
from .env_rewards import terminal_reward
from .env_utils import action_mask, action_space, observation_space, select_action
from .observation import to_numeric_observation
from .players import player_ids
from .setup_game import create_game_state


class TableAECEnv(AECEnv):
    """Table-mode AEC env; terminal rewards per ``env_rewards``, set once."""

    metadata = {"name": "nuclear_war_table_v1"}

    def __init__(
        self,
        seed: int | None = None,
        max_cycles: int = 50,
        players: int = 2,
    ) -> None:
        super().__init__()
        self._seed = seed
        self.max_cycles = validate_max_cycles(max_cycles)
        self.possible_agents = player_ids(players)
        self.action_spaces = {agent: action_space() for agent in self.possible_agents}
        self.observation_spaces = {
            agent: observation_space() for agent in self.possible_agents
        }
        self.reset(seed=seed)

    def reset(
        self,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> None:
        resolved_seed = self._seed if seed is None else seed
        self.game_state = create_game_state(
            "table",
            len(self.possible_agents),
            resolved_seed,
            defer_opening_commitment=True,
        )
        self.agents = list(self.possible_agents)
        self.rewards = {agent: 0.0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0.0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {agent: False for agent in self.agents}
        self.infos = {agent: {} for agent in self.agents}
        self._cycle_count = 0
        self._agent_selector = AgentSelector(self.agents)
        batch = start_game(self.game_state)
        for event, _turn in batch.events:
            key = event.player_id or self.agents[0]
            events = self.infos.setdefault(key, {}).setdefault("events", [])
            events.append(event.event_type)
        self._select_pending_agent()

    def step(self, action: object | None) -> None:
        agent = self.agent_selection
        self._clear_rewards()
        if self.terminations[agent] or self.truncations[agent]:
            self._was_dead_step(action)
            return
        decision = pending_decision(self.game_state)
        if decision is None:
            self._mark_done_if_needed()
            self._select_pending_agent()
            self._accumulate_rewards()
            return
        if decision.agent_id != agent:
            self.agent_selection = decision.agent_id
            self._accumulate_rewards()
            return
        if action is None:
            raise ValueError(f"Missing action for live agent {agent}")
        selected = select_action(decision.options, action)
        batch = apply_decision_result(self.game_state, selected)
        self.infos[agent] = {
            "events": [event.event_type for event, _turn in batch.events]
        }
        self._sync_cycle_count()
        self._mark_done_if_needed()
        self._select_pending_agent()
        self._accumulate_rewards()

    def observe(self, agent: str) -> dict:
        values = to_numeric_observation(self.game_state, agent)
        obs = {
            "observation": np.array(values, dtype=np.float32),
            "action_mask": action_mask(self._pending_options_for(agent)),
        }
        if self.terminations.get(agent, False) or self.truncations.get(agent, False):
            obs["action_mask"][:] = 0
        return obs

    def action_space(self, agent: str) -> Any:
        return self.action_spaces[agent]

    def observation_space(self, agent: str) -> Any:
        return self.observation_spaces[agent]

    def _mark_done_if_needed(self) -> None:
        done = game_over(self.game_state)
        for agent in self.agents:
            player = self.game_state.players[agent]
            terminated = done or (
                not player.alive and not player_final_strike_pending(player)
            )
            if terminated and not self.terminations[agent]:
                self.terminations[agent] = True
                self.rewards[agent] = terminal_reward(player, done)
        if self._cycle_count >= self.max_cycles:
            for agent in self.agents:
                self.truncations[agent] = True

    def _select_pending_agent(self) -> None:
        decision = pending_decision(self.game_state)
        if decision is not None:
            self.agent_selection = decision.agent_id
            return
        self.agent_selection = self._agent_selector.next()

    def _pending_options_for(self, agent: str) -> list[LegalAction]:
        decision = pending_decision(self.game_state)
        if decision is None or decision.agent_id != agent:
            return []
        return decision.options

    def _sync_cycle_count(self) -> None:
        cursor = self.game_state.cursor
        if cursor is None:
            return
        completed_round = max(0, cursor.round - 1)
        if completed_round > self._cycle_count:
            self._cycle_count = completed_round
            self.game_state.turn = completed_round


__all__ = ["TableAECEnv"]
