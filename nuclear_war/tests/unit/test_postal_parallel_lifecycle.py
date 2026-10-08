"""Postal Parallel environment lifecycle tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.env_postal import PostalParallelEnv


def test_parallel_step_requires_reset_before_use() -> None:
    env = PostalParallelEnv(seed=0)

    with pytest.raises(ValueError, match="Environment must be reset before stepping"):
        env.step({})


def test_parallel_step_rejects_step_after_environment_end() -> None:
    env = PostalParallelEnv(seed=0)
    env.reset()
    env.agents = []

    with pytest.raises(ValueError, match="Cannot step after environment has ended"):
        env.step({})


def test_parallel_step_advances_engine_turn() -> None:
    env = PostalParallelEnv(seed=0)
    env.reset()

    assert env.game_state.turn == 0

    observations, _, _, _, _ = env.step({"player_0": 0, "player_1": 0})

    assert env.game_state.turn == 1
    assert observations["player_0"]["observation"][0] == 1


def test_parallel_step_removes_eliminated_player_without_final_strike() -> None:
    env = PostalParallelEnv(seed=0, players=3)
    env.reset()
    env.game_state.players["player_2"].alive = False
    env.game_state.players["player_2"].population = []

    observations, rewards, terminations, _, _ = env.step(
        {"player_0": 0, "player_1": 0, "player_2": 0}
    )

    assert terminations["player_2"] is True
    assert rewards["player_2"] == -1.0
    # The eliminated agent acted this step, so it still receives its final
    # observation; it drops out of the live agent list afterwards.
    assert set(observations) == {"player_0", "player_1", "player_2"}
    assert env.agents == ["player_0", "player_1"]
