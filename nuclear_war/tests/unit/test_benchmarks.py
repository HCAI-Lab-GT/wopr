"""Benchmark guardrail tests."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[2] / "benchmarks" / "run_benchmarks.py"
if str(MODULE_PATH.parent) not in sys.path:
    sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("run_benchmarks", MODULE_PATH)
assert SPEC is not None
run_benchmarks = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(run_benchmarks)


def test_benchmark_comparison_ignores_single_outlier() -> None:
    baseline = {"metrics": {"phase0_main_ms": 0.25}}
    current = {
        "metrics": {"phase0_main_ms": 0.60},
        "timeline": [
            {"elapsed_ms": 0.10},
            {"elapsed_ms": 0.11},
            {"elapsed_ms": 0.12},
            {"elapsed_ms": 2.50},
        ],
    }
    assert run_benchmarks._compare_metrics(current, baseline, threshold=0.9) is True


def test_benchmark_comparison_accepts_v1_guardrail_metric_name() -> None:
    baseline = {"metrics": {"guardrail_main_ms": 0.25}}
    current = {
        "metrics": {"guardrail_main_ms": 0.20},
        "timeline": [{"elapsed_ms": 0.20}],
    }
    assert run_benchmarks._compare_metrics(current, baseline, threshold=0.9) is True


def test_benchmark_comparison_ignores_guardrail_micro_jitter() -> None:
    baseline = {"metrics": {"guardrail_main_ms": 0.10}}
    current = {
        "metrics": {"guardrail_main_ms": 0.30},
        "timeline": [{"elapsed_ms": 0.30}],
    }
    assert run_benchmarks._compare_metrics(current, baseline, threshold=0.9) is True


def test_benchmark_comparison_rejects_sustained_slowdown() -> None:
    baseline = {"metrics": {"phase0_main_ms": 0.25}}
    current = {
        "metrics": {"phase0_main_ms": 0.60},
        "timeline": [
            {"elapsed_ms": 0.60},
            {"elapsed_ms": 0.61},
            {"elapsed_ms": 0.59},
            {"elapsed_ms": 0.62},
        ],
    }
    assert run_benchmarks._compare_metrics(current, baseline, threshold=0.9) is False


def test_benchmark_comparison_rejects_v1_simulation_slowdown() -> None:
    baseline = {
        "metrics": {
            "phase0_main_ms": 0.25,
            "table_simulation_ms": 1.0,
            "postal_simulation_ms": 1.0,
        }
    }
    current = {
        "metrics": {
            "phase0_main_ms": 0.20,
            "table_simulation_ms": 5.0,
            "postal_simulation_ms": 1.0,
        },
        "timeline": [{"elapsed_ms": 0.20}],
    }
    assert run_benchmarks._compare_metrics(current, baseline, threshold=0.9) is False


def test_benchmark_comparison_ignores_sub_millisecond_v1_jitter() -> None:
    baseline = {
        "metrics": {
            "phase0_main_ms": 0.25,
            "table_simulation_ms": 0.50,
            "postal_simulation_ms": 0.75,
        }
    }
    current = {
        "metrics": {
            "phase0_main_ms": 0.20,
            "table_simulation_ms": 0.62,
            "postal_simulation_ms": 0.98,
        },
        "timeline": [{"elapsed_ms": 0.20}],
    }
    assert run_benchmarks._compare_metrics(current, baseline, threshold=0.9) is True


def test_benchmark_comparison_ignores_small_absolute_simulation_jitter() -> None:
    baseline = {
        "metrics": {
            "phase0_main_ms": 0.25,
            "table_simulation_ms": 0.50,
            "postal_simulation_ms": 0.75,
        }
    }
    current = {
        "metrics": {
            "phase0_main_ms": 0.20,
            "table_simulation_ms": 1.90,
            "postal_simulation_ms": 2.40,
        },
        "timeline": [{"elapsed_ms": 0.20}],
    }
    assert run_benchmarks._compare_metrics(current, baseline, threshold=0.9) is True


def test_benchmark_payload_includes_table_and_postal_simulation(tmp_path: Path) -> None:
    config = run_benchmarks.AppConfig(
        seed=3,
        data_dir=tmp_path / "data",
        benchmark_output=tmp_path / "latest.json",
    )
    limits = run_benchmarks.V1Limits(
        bench_baseline=tmp_path / "baseline.json",
        docs_output_dir=tmp_path / "docs",
    )
    payload = run_benchmarks.run(loops=1, limits=limits, config=config)
    metrics = payload["metrics"]
    pie = payload["pie"]
    assert "guardrail_main_ms" in metrics
    assert "table_simulation_ms" in metrics
    assert "postal_simulation_ms" in metrics
    assert "table_simulation_ms" in pie
    assert "postal_simulation_ms" in pie


def test_saved_benchmark_baseline_includes_v1_simulation_metrics() -> None:
    payload = json.loads(
        Path("benchmarks/baselines/v1_guardrails.json").read_text(encoding="utf-8")
    )
    metrics = payload["metrics"]
    assert "guardrail_main_ms" in metrics
    assert "table_simulation_ms" in metrics
    assert "postal_simulation_ms" in metrics
