"""Central bootstrap helpers for Nuclear War v1 guardrails."""

from __future__ import annotations

from .config import DEFAULT_CONFIG, AppConfig
from .constants import DEFAULT_LIMITS, V1Limits


def ensure_directories(config: AppConfig, limits: V1Limits) -> None:
    """Create directories required for local v1 tooling."""
    config.data_dir.mkdir(parents=True, exist_ok=True)
    limits.bench_baseline.parent.mkdir(parents=True, exist_ok=True)
    config.benchmark_output.parent.mkdir(parents=True, exist_ok=True)
    limits.docs_output_dir.mkdir(parents=True, exist_ok=True)


def main(config: AppConfig | None = None, limits: V1Limits | None = None) -> None:
    """Prepare local v1 guardrail directories."""
    resolved_config = config or DEFAULT_CONFIG
    resolved_limits = limits or DEFAULT_LIMITS
    ensure_directories(resolved_config, resolved_limits)
    marker = resolved_limits.docs_output_dir / "v1_guardrails.txt"
    marker.write_text("Nuclear War v1 guardrails ready.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
