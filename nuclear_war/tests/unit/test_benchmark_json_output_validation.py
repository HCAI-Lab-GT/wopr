"""Benchmark JSON output validation tests."""

from __future__ import annotations

import importlib.util
import math
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


def test_write_json_rejects_non_finite_metric_values(tmp_path: Path) -> None:
    output_path = tmp_path / "latest.json"
    payload = {"metrics": {"guardrail_main_ms": math.nan}}

    with pytest.raises(
        ValueError,
        match="Out of range float values are not JSON compliant",
    ):
        run_benchmarks._write_json(output_path, payload)


def test_load_json_rejects_non_standard_constants(tmp_path: Path) -> None:
    baseline_path = tmp_path / "baseline.json"
    baseline_path.write_text(
        '{"metrics": {"guardrail_main_ms": NaN}}',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Invalid JSON constant: NaN"):
        run_benchmarks._load_json(baseline_path)
