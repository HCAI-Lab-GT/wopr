"""Application configuration utilities."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Immutable configuration for local v1 tooling."""

    seed: int
    data_dir: Path
    benchmark_output: Path

    @staticmethod
    def from_env() -> AppConfig:
        """Build configuration from environment variables with defaults."""
        seed = _env_int("NUCLEAR_WAR_SEED", "0")
        data_root = Path(os.environ.get("NUCLEAR_WAR_DATA", "data"))
        bench_out = Path(
            os.environ.get("NUCLEAR_WAR_BENCH_OUT", "benchmarks/results/latest.json"),
        )
        return AppConfig(seed=seed, data_dir=data_root, benchmark_output=bench_out)


def _env_int(name: str, default: str) -> int:
    value = os.environ.get(name, default)
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


DEFAULT_CONFIG = AppConfig.from_env()

__all__ = ["AppConfig", "DEFAULT_CONFIG"]
