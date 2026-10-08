"""Player-count validation tests."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_env.env_postal import PostalParallelEnv
from nuclear_war_env.env_table import TableAECEnv
from nuclear_war_env.players import player_ids
from nuclear_war_env.setup_game import create_game_state


def test_player_ids_rejects_non_integer_count() -> None:
    malformed_count: Any = "2"

    with pytest.raises(ValueError, match="Player count must be an integer"):
        player_ids(malformed_count)


def test_create_game_state_rejects_non_integer_count_before_loading_rules(
    monkeypatch,
) -> None:
    malformed_count: Any = "2"

    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid player count")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )

    with pytest.raises(ValueError, match="Player count must be an integer"):
        create_game_state("table", player_count=malformed_count, seed=0)


def test_table_env_rejects_non_integer_player_count() -> None:
    malformed_count: Any = "2"

    with pytest.raises(ValueError, match="Player count must be an integer"):
        TableAECEnv(seed=1, players=malformed_count)


def test_postal_env_rejects_non_integer_player_count() -> None:
    malformed_count: Any = "2"

    with pytest.raises(ValueError, match="Player count must be an integer"):
        PostalParallelEnv(seed=1, players=malformed_count)


def test_postal_env_supports_three_player_games() -> None:
    env = PostalParallelEnv(seed=1, players=3)

    observations, _ = env.reset()
    next_observations, rewards, terminations, truncations, _ = env.step(
        {"player_0": 0, "player_1": 0, "player_2": 0}
    )

    assert env.possible_agents == ["player_0", "player_1", "player_2"]
    assert set(observations) == set(env.possible_agents)
    assert set(next_observations) == set(env.possible_agents)
    assert set(rewards) == set(env.possible_agents)
    assert not any(terminations.values())
    assert not any(truncations.values())
