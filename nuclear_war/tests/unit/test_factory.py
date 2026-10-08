"""Environment factory tests."""

from __future__ import annotations

import pytest

from nuclear_war_env import factory
from nuclear_war_env.env_postal import PostalParallelEnv
from nuclear_war_env.env_stub_aec import Phase0AECEnv
from nuclear_war_env.env_stub_parallel import Phase0ParallelEnv
from nuclear_war_env.env_table import TableAECEnv


def test_default_factories_create_real_v1_envs() -> None:
    assert isinstance(factory.create_aec_env(seed=1), TableAECEnv)
    assert isinstance(factory.create_parallel_env(seed=1), PostalParallelEnv)


def test_phase0_factories_keep_legacy_stubs_available() -> None:
    assert isinstance(factory.create_phase0_aec_env(seed=1), Phase0AECEnv)
    assert isinstance(factory.create_phase0_parallel_env(seed=1), Phase0ParallelEnv)


def test_postal_factory_rejects_press_mode() -> None:
    with pytest.raises(ValueError, match="Postal press is deferred"):
        factory.create_postal_env(seed=1, press=True)


def test_aec_factory_supports_configured_player_count() -> None:
    env = factory.create_aec_env(seed=1, players=3)

    assert env.possible_agents == ["player_0", "player_1", "player_2"]


def test_table_factory_supports_configured_player_count() -> None:
    env = factory.create_table_env(seed=1, players=3)

    assert env.possible_agents == ["player_0", "player_1", "player_2"]


def test_parallel_factory_supports_configured_player_count() -> None:
    env = factory.create_parallel_env(seed=1, players=3)

    assert env.possible_agents == ["player_0", "player_1", "player_2"]


def test_postal_factory_supports_configured_player_count() -> None:
    env = factory.create_postal_env(seed=1, players=3)

    assert env.possible_agents == ["player_0", "player_1", "player_2"]
