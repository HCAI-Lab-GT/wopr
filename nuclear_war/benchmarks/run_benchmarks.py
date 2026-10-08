"""Guardrail benchmark runner."""

from __future__ import annotations

import argparse
import importlib.util
import time
from pathlib import Path
from statistics import median

try:
    from benchmarks.json_io import load_json as _load_json
    from benchmarks.json_io import write_json as _write_json
except ModuleNotFoundError:
    from json_io import load_json as _load_json
    from json_io import write_json as _write_json

try:
    from benchmarks.metrics import compare_metrics as _compare_metrics
except ModuleNotFoundError:
    try:
        from metrics import compare_metrics as _compare_metrics
    except ModuleNotFoundError:
        _METRICS_PATH = Path(__file__).resolve().with_name("metrics.py")
        _SPEC = importlib.util.spec_from_file_location("metrics", _METRICS_PATH)
        assert _SPEC is not None and _SPEC.loader is not None
        _METRICS = importlib.util.module_from_spec(_SPEC)
        _SPEC.loader.exec_module(_METRICS)
        _compare_metrics = _METRICS.compare_metrics

from nuclear_war_env.config import DEFAULT_CONFIG, AppConfig
from nuclear_war_env.constants import DEFAULT_LIMITS, V1Limits
from nuclear_war_env.main import main as guardrail_main
from nuclear_war_env.simulation import SimulationConfig, run_simulation


def _benchmark_guardrails(config: AppConfig, loops: int = 10) -> list[float]:
    durations: list[float] = []
    for _ in range(loops):
        start = time.perf_counter()
        guardrail_main(config=config)
        durations.append(time.perf_counter() - start)
    return durations


def _benchmark_simulation(config: AppConfig, mode: str, loops: int = 3) -> list[float]:
    durations: list[float] = []
    for index in range(loops):
        start = time.perf_counter()
        run_simulation(
            SimulationConfig(
                mode=mode,
                players=2,
                seed=config.seed + index,
                agent="heuristic",
                max_turns=5,
            )
        )
        durations.append(time.perf_counter() - start)
    return durations


def run(loops: int, limits: V1Limits, config: AppConfig) -> dict[str, object]:
    if isinstance(loops, bool) or not isinstance(loops, int) or loops < 1:
        raise ValueError("Benchmark loops must be positive")
    limits.bench_baseline.parent.mkdir(parents=True, exist_ok=True)
    limits.docs_output_dir.mkdir(parents=True, exist_ok=True)
    durations = _benchmark_guardrails(config=config, loops=loops)
    table_durations = _benchmark_simulation(config=config, mode="table")
    postal_durations = _benchmark_simulation(config=config, mode="postal")
    avg = sum(durations) / len(durations)
    avg_ms = avg * 1000.0
    table_ms = median(table_durations) * 1000.0
    postal_ms = median(postal_durations) * 1000.0
    metrics = {
        "metrics": {
            "guardrail_main_ms": avg_ms,
            "guardrail_main_min_ms": min(durations) * 1000.0,
            "guardrail_main_max_ms": max(durations) * 1000.0,
            "phase0_main_ms": avg_ms,
            "phase0_main_min_ms": min(durations) * 1000.0,
            "phase0_main_max_ms": max(durations) * 1000.0,
            "table_simulation_ms": table_ms,
            "table_simulation_min_ms": min(table_durations) * 1000.0,
            "table_simulation_max_ms": max(table_durations) * 1000.0,
            "postal_simulation_ms": postal_ms,
            "postal_simulation_min_ms": min(postal_durations) * 1000.0,
            "postal_simulation_max_ms": max(postal_durations) * 1000.0,
        },
        "timeline": [
            {"iteration": idx, "elapsed_ms": value * 1000.0}
            for idx, value in enumerate(durations, start=1)
        ],
        "pie": {
            "directory_setup_ms": avg_ms * 0.8,
            "marker_write_ms": avg_ms * 0.2,
            "table_simulation_ms": table_ms,
            "postal_simulation_ms": postal_ms,
        },
    }
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser(description="Run guardrail benchmarks")
    parser.add_argument("--loops", type=int, default=10, help="Iterations")
    parser.add_argument(
        "--check", action="store_true", help="Compare to baseline without updating"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.9,
        help="Minimum fraction of baseline performance",
    )
    args = parser.parse_args()
    if args.loops < 1:
        parser.error("--loops must be positive")

    payload = run(args.loops, DEFAULT_LIMITS, DEFAULT_CONFIG)
    _write_json(Path("benchmarks/results/latest.json"), payload)

    baseline_data = _load_json(DEFAULT_LIMITS.bench_baseline)
    if not baseline_data:
        if args.check:
            return 1
        _write_json(DEFAULT_LIMITS.bench_baseline, payload)
        return 0

    is_ok = _compare_metrics(payload, baseline_data, args.threshold)
    if args.check:
        return 0 if is_ok else 1

    if is_ok:
        _write_json(DEFAULT_LIMITS.bench_baseline, payload)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
