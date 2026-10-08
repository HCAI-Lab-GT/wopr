"""Phase 0 scaffolding smoke tests."""

import importlib.util
from pathlib import Path

from nuclear_war_env.config import AppConfig
from nuclear_war_env.constants import DEFAULT_LIMITS, Phase0Limits, V1Limits
from nuclear_war_env.main import main as run_main

_BENCHMARKS = Path("benchmarks/run_benchmarks.py")
_SPEC = importlib.util.spec_from_file_location("run_benchmarks", _BENCHMARKS)
assert _SPEC is not None and _SPEC.loader is not None
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def test_phase0_limits_defaults() -> None:
    assert DEFAULT_LIMITS.max_file_lines == 150
    assert DEFAULT_LIMITS.bench_baseline == Path(
        "benchmarks/baselines/v1_guardrails.json"
    )
    assert DEFAULT_LIMITS.docs_output_dir == Path("build/docs")


def test_v1_limits_is_canonical_limit_type() -> None:
    limits = V1Limits()
    assert isinstance(DEFAULT_LIMITS, V1Limits)
    assert isinstance(limits, Phase0Limits)
    assert limits.max_file_lines == 150


def test_app_config_from_env_defaults(monkeypatch) -> None:
    monkeypatch.delenv("NUCLEAR_WAR_SEED", raising=False)
    monkeypatch.delenv("NUCLEAR_WAR_DATA", raising=False)
    monkeypatch.delenv("NUCLEAR_WAR_BENCH_OUT", raising=False)
    config = AppConfig.from_env()
    assert config.seed == 0
    assert config.data_dir == Path("data")
    assert config.benchmark_output == Path("benchmarks/results/latest.json")


def test_main_creates_directories(tmp_path) -> None:
    custom_config = AppConfig(
        seed=7,
        data_dir=tmp_path / "data",
        benchmark_output=tmp_path / "bench" / "results.json",
    )
    custom_limits = Phase0Limits(
        max_file_lines=150,
        bench_baseline=tmp_path / "baseline" / "phase0.json",
        docs_output_dir=tmp_path / "docs",
    )
    run_main(config=custom_config, limits=custom_limits)
    assert custom_config.data_dir.exists()
    assert custom_limits.bench_baseline.parent.exists()
    marker = custom_limits.docs_output_dir / "v1_guardrails.txt"
    assert marker.exists()
    assert "Nuclear War v1 guardrails ready" in marker.read_text(encoding="utf-8")


def test_benchmarks_include_v1_simulation_metric(tmp_path) -> None:
    config = AppConfig(
        seed=1,
        data_dir=tmp_path / "data",
        benchmark_output=tmp_path / "bench" / "results.json",
    )
    limits = Phase0Limits(
        max_file_lines=150,
        bench_baseline=tmp_path / "baseline" / "phase0.json",
        docs_output_dir=tmp_path / "docs",
    )
    payload = _MODULE.run(loops=1, limits=limits, config=config)
    assert "table_simulation_ms" in payload["metrics"]
