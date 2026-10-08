"""Seed validation tests."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_env.env_postal import PostalParallelEnv
from nuclear_war_env.env_table import TableAECEnv
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.setup_game import create_game_state


@pytest.mark.parametrize("seed", ["1", 1.5, True, b"1"])
def test_seeded_rng_rejects_malformed_seed(seed: Any) -> None:
    with pytest.raises(ValueError, match="Seed must be an integer or None"):
        SeededRNG(seed)


def test_seeded_rng_rejects_boolean_sample_count() -> None:
    count: Any = True

    with pytest.raises(ValueError, match="Sample count must be an integer"):
        SeededRNG(seed=1).sample([1, 2, 3], count)


def test_seeded_rng_rejects_boolean_randint_bound() -> None:
    lower: Any = True

    with pytest.raises(ValueError, match="Random integer bounds must be integers"):
        SeededRNG(seed=1).randint(lower, 3)


def test_seeded_rng_rejects_boolean_spawn_salt() -> None:
    salt: Any = True

    with pytest.raises(ValueError, match="Spawn salt must be an integer"):
        SeededRNG(seed=1).spawn(salt)


def test_create_game_state_rejects_malformed_seed_before_loading_rules(
    monkeypatch,
) -> None:
    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid seed")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    malformed_seed: Any = "1"

    with pytest.raises(ValueError, match="Seed must be an integer or None"):
        create_game_state("table", player_count=2, seed=malformed_seed)


def test_table_env_rejects_malformed_constructor_seed() -> None:
    malformed_seed: Any = "1"

    with pytest.raises(ValueError, match="Seed must be an integer or None"):
        TableAECEnv(seed=malformed_seed)


def test_postal_env_rejects_malformed_constructor_seed() -> None:
    malformed_seed: Any = "1"

    with pytest.raises(ValueError, match="Seed must be an integer or None"):
        PostalParallelEnv(seed=malformed_seed)


def test_table_env_reset_rejects_malformed_seed() -> None:
    env = TableAECEnv(seed=1)
    malformed_seed: Any = "2"

    with pytest.raises(ValueError, match="Seed must be an integer or None"):
        env.reset(seed=malformed_seed)


def test_postal_env_reset_rejects_boolean_seed() -> None:
    env = PostalParallelEnv(seed=1)
    malformed_seed: Any = True

    with pytest.raises(ValueError, match="Seed must be an integer or None"):
        env.reset(seed=malformed_seed)
