"""Factory helpers for creating Nuclear War environments."""

from __future__ import annotations

from .env_postal import PostalParallelEnv
from .env_stub_aec import Phase0AECEnv
from .env_stub_parallel import Phase0ParallelEnv
from .env_table import TableAECEnv


def create_aec_env(
    seed: int | None = None,
    max_cycles: int = 50,
    players: int = 2,
) -> TableAECEnv:
    """Return the v1 table-mode AEC environment."""
    return TableAECEnv(seed=seed, max_cycles=max_cycles, players=players)


def create_parallel_env(
    seed: int | None = None,
    max_cycles: int = 50,
    players: int = 2,
) -> PostalParallelEnv:
    """Return the v1 postal-mode Parallel environment."""
    return PostalParallelEnv(seed=seed, max_cycles=max_cycles, players=players)


def create_phase0_aec_env(
    seed: int | None = None,
    max_cycles: int = 2,
) -> Phase0AECEnv:
    """Return the legacy Phase 0 AEC stub environment."""
    return Phase0AECEnv(seed=seed, max_cycles=max_cycles)


def create_phase0_parallel_env(
    seed: int | None = None,
    max_cycles: int = 2,
) -> Phase0ParallelEnv:
    """Return the legacy Phase 0 Parallel stub environment."""
    return Phase0ParallelEnv(seed=seed, max_cycles=max_cycles)


def create_table_env(
    seed: int | None = None,
    players: int = 2,
    max_cycles: int = 50,
) -> TableAECEnv:
    """Return the v1 table-mode AEC environment."""
    return TableAECEnv(seed=seed, players=players, max_cycles=max_cycles)


def create_postal_env(
    seed: int | None = None,
    press: bool = False,
    players: int = 2,
    max_cycles: int = 50,
) -> PostalParallelEnv:
    """Return the v1 postal-mode Parallel environment."""
    return PostalParallelEnv(
        seed=seed,
        press=press,
        players=players,
        max_cycles=max_cycles,
    )


__all__ = [
    "create_aec_env",
    "create_parallel_env",
    "create_phase0_aec_env",
    "create_phase0_parallel_env",
    "create_table_env",
    "create_postal_env",
    "Phase0AECEnv",
    "Phase0ParallelEnv",
    "TableAECEnv",
    "PostalParallelEnv",
]
