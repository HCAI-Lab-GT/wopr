"""Environment max-cycle validation tests."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_env import factory
from nuclear_war_env.env_postal import PostalParallelEnv
from nuclear_war_env.env_table import TableAECEnv


def test_table_env_rejects_non_integer_max_cycles() -> None:
    malformed_cycles: Any = "50"

    with pytest.raises(ValueError, match="Environment max_cycles must be an integer"):
        TableAECEnv(seed=1, max_cycles=malformed_cycles)


def test_postal_env_rejects_non_positive_max_cycles() -> None:
    with pytest.raises(ValueError, match="Environment max_cycles must be positive"):
        PostalParallelEnv(seed=1, max_cycles=0)


def test_aec_factory_rejects_non_positive_max_cycles() -> None:
    with pytest.raises(ValueError, match="Environment max_cycles must be positive"):
        factory.create_aec_env(seed=1, max_cycles=0)


def test_table_factory_rejects_non_positive_max_cycles() -> None:
    with pytest.raises(ValueError, match="Environment max_cycles must be positive"):
        factory.create_table_env(seed=1, max_cycles=0)


def test_parallel_factory_rejects_non_integer_max_cycles() -> None:
    malformed_cycles: Any = "50"

    with pytest.raises(ValueError, match="Environment max_cycles must be an integer"):
        factory.create_parallel_env(seed=1, max_cycles=malformed_cycles)


def test_postal_factory_rejects_non_integer_max_cycles() -> None:
    malformed_cycles: Any = "50"

    with pytest.raises(ValueError, match="Environment max_cycles must be an integer"):
        factory.create_postal_env(seed=1, max_cycles=malformed_cycles)
