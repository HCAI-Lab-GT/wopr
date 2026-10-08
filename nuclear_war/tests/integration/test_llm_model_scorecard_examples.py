"""Tests for checked-in model scorecard examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nuclear_war_env.cli import main
from nuclear_war_env.llm_model_scorecard_catalog import load_catalog_rows

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_PATH = PROJECT_ROOT / "docs/examples/llm_model_scorecard_catalog_demo.json"
CATALOG_RELATIVE_PATH = (
    "research/llm_model_calibration/data/serverless_catalog_2026-07-05.json"
)


def test_scorecard_catalog_demo_writes_predicted_only_artifacts(
    tmp_path,
    capsys,
) -> None:
    demo = _load_demo()
    assert demo["command"] == "llm-model-scorecard"
    assert demo["stage"] == "catalog"
    assert demo["catalog"] == CATALOG_RELATIVE_PATH

    catalog_path = PROJECT_ROOT / str(demo["catalog"])
    rows = load_catalog_rows(catalog_path)
    assert len(rows) == 23

    out_dir = tmp_path / "scorecard"
    code = main(_demo_args(demo, out_dir))

    captured = capsys.readouterr()
    catalog = json.loads((out_dir / "catalog_scorecard.json").read_text())
    stage2 = json.loads((out_dir / "stage2_calibration_results.json").read_text())
    assert code == 0
    assert json.loads(captured.out) == _expected_paths(out_dir)
    assert len(catalog["scores"]) == 23
    assert {row["score_type"] for row in catalog["scores"]} == {"predicted"}
    assert stage2["results"] == []
    assert (out_dir / "scorecard_summary.md").is_file()


def _load_demo() -> dict[str, Any]:
    return json.loads(EXAMPLE_PATH.read_text(encoding="utf-8"))


def _demo_args(demo: dict[str, Any], out_dir: Path) -> list[str]:
    return [
        str(demo["command"]),
        "--stage",
        str(demo["stage"]),
        "--catalog",
        str(PROJECT_ROOT / str(demo["catalog"])),
        "--out",
        str(out_dir),
    ]


def _expected_paths(out_dir: Path) -> dict[str, str]:
    return {
        "catalog_scorecard": str(out_dir / "catalog_scorecard.json"),
        "scorecard_summary": str(out_dir / "scorecard_summary.md"),
        "stage2_calibration_results": str(out_dir / "stage2_calibration_results.json"),
    }
