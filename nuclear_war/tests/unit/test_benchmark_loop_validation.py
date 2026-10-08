"""Benchmark loop validation tests."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[2] / "benchmarks" / "run_benchmarks.py"
if str(MODULE_PATH.parent) not in sys.path:
    sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("run_benchmarks", MODULE_PATH)
assert SPEC is not None
run_benchmarks = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(run_benchmarks)


def test_benchmark_run_rejects_zero_loops(tmp_path) -> None:
    config = run_benchmarks.AppConfig(
        seed=3,
        data_dir=tmp_path / "data",
        benchmark_output=tmp_path / "latest.json",
    )
    limits = run_benchmarks.V1Limits(
        bench_baseline=tmp_path / "baseline.json",
        docs_output_dir=tmp_path / "docs",
    )

    with pytest.raises(ValueError, match="Benchmark loops must be positive"):
        run_benchmarks.run(loops=0, limits=limits, config=config)


def test_benchmark_run_rejects_boolean_loops(tmp_path) -> None:
    config = run_benchmarks.AppConfig(
        seed=3,
        data_dir=tmp_path / "data",
        benchmark_output=tmp_path / "latest.json",
    )
    limits = run_benchmarks.V1Limits(
        bench_baseline=tmp_path / "baseline.json",
        docs_output_dir=tmp_path / "docs",
    )

    with pytest.raises(ValueError, match="Benchmark loops must be positive"):
        run_benchmarks.run(loops=True, limits=limits, config=config)


def test_benchmark_main_rejects_zero_loops(monkeypatch, capsys) -> None:
    monkeypatch.setattr(sys, "argv", ["run_benchmarks.py", "--loops", "0"])

    with pytest.raises(SystemExit) as exc_info:
        run_benchmarks.main()

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert "--loops must be positive" in captured.err
