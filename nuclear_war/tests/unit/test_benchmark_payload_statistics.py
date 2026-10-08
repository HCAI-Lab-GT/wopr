"""Benchmark payload statistic tests."""

from __future__ import annotations

import importlib.util
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


def test_benchmark_payload_uses_median_simulation_timing(monkeypatch, tmp_path) -> None:
    def fake_guardrails(*, config, loops):
        return [0.0001 for _ in range(loops)]

    def fake_simulation(*, config, mode, loops=3):
        if mode == "table":
            return [0.0005, 0.0007, 0.0050]
        return [0.0008, 0.0010, 0.0012]

    monkeypatch.setattr(run_benchmarks, "_benchmark_guardrails", fake_guardrails)
    monkeypatch.setattr(run_benchmarks, "_benchmark_simulation", fake_simulation)
    config = run_benchmarks.AppConfig(
        seed=3,
        data_dir=tmp_path / "data",
        benchmark_output=tmp_path / "latest.json",
    )
    limits = run_benchmarks.V1Limits(
        bench_baseline=tmp_path / "baseline.json",
        docs_output_dir=tmp_path / "docs",
    )

    payload = run_benchmarks.run(loops=3, limits=limits, config=config)

    assert payload["metrics"]["table_simulation_ms"] == 0.7
    assert payload["metrics"]["postal_simulation_ms"] == 1.0
