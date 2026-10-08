"""Full-game reward and terminal-observation behavior for the v1 environments.

Reward scheme (see nuclear_war_env.env_rewards): +1 to each survivor at game
end, -1 to a player at the step its elimination becomes final, 0 otherwise
(including truncation).
"""

from __future__ import annotations

import numpy as np

from nuclear_war_env.factory import create_postal_env, create_table_env


def _first_legal(mask: np.ndarray) -> int:
    legal = np.flatnonzero(mask)
    return int(legal[0]) if legal.size else 0


def _last_legal(mask: np.ndarray) -> int:
    legal = np.flatnonzero(mask)
    return int(legal[-1]) if legal.size else 0


def test_table_env_full_game_assigns_terminal_rewards() -> None:
    # Seed re-pinned from 42 to 2 by the attack/retaliation fidelity fixes: the
    # wider final-retaliation pool turns seed 42 into a mutual annihilation (all -1),
    # which no longer exercises the +1 survivor reward. Seed 2 still ends with a
    # single survivor under first-legal play, keeping both reward signs covered.
    env = create_table_env(seed=2, players=3, max_cycles=500)
    env.reset()
    final_rewards: dict[str, float] = {}
    for agent in env.agent_iter(max_iter=200_000):
        observation, reward, termination, truncation, _info = env.last()
        if termination or truncation:
            final_rewards[agent] = reward
            env.step(None)
            continue
        assert observation is not None
        env.step(_first_legal(observation["action_mask"]))

    assert set(final_rewards) == set(env.possible_agents)
    assert not any(env.truncations.values()), "game must end by elimination"
    values = sorted(final_rewards.values())
    assert values == [-1.0, -1.0, 1.0]


def test_postal_env_full_game_final_observations_and_rewards() -> None:
    # seed 3 + last-legal actions is a policy known to end by elimination.
    env = create_postal_env(seed=3, players=3, max_cycles=200)
    observations, _ = env.reset()
    final_rewards: dict[str, float] = {}
    truncated_any = False
    while env.agents:
        acting = list(env.agents)
        actions: dict[str, object] = {
            agent: _last_legal(observations[agent]["action_mask"]) for agent in acting
        }
        observations, rewards, terminations, truncations, _infos = env.step(actions)
        # Every agent that acted this step must be reported, dead agents from
        # earlier steps must not reappear, and each acting agent must receive
        # an observation — including on its terminal step.
        for mapping in (observations, rewards, terminations, truncations):
            assert set(mapping) == set(acting)
        for agent in acting:
            if terminations[agent]:
                final_rewards[agent] = rewards[agent]
            truncated_any = truncated_any or truncations[agent]

    assert not truncated_any, "game must end by elimination"
    assert set(final_rewards) == set(env.possible_agents)
    values = sorted(final_rewards.values())
    assert values == [-1.0, -1.0, 1.0]
