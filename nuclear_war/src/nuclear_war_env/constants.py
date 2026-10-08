"""Central constants for local v1 guardrails."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class V1Limits:
    """Holds static limits for local v1 guardrails."""

    max_file_lines: int = 150
    bench_baseline: Path = Path("benchmarks/baselines/v1_guardrails.json")
    docs_output_dir: Path = Path("build/docs")


Phase0Limits = V1Limits
DEFAULT_LIMITS = V1Limits()

__all__ = ["DEFAULT_LIMITS", "Phase0Limits", "V1Limits"]
