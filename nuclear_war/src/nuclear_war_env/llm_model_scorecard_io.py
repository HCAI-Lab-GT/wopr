"""Artifact IO for serverless model scorecards."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .llm_model_scorecard_catalog import CatalogScore
from .llm_model_scorecard_io_support import (
    SCHEMA_VERSION,
    public_payload,
    read_json,
    validate_no_secret_fields,
    validate_payload,
    write_json,
)
from .llm_model_scorecard_stage2 import Stage2ModelResult

CATALOG_SCORECARD_FILE = "catalog_scorecard.json"
STAGE2_RESULTS_FILE = "stage2_calibration_results.json"
SCORECARD_SUMMARY_FILE = "scorecard_summary.md"

_CATALOG_FIELDS = {"schema_version", "scores"}
_STAGE2_FIELDS = {"schema_version", "results"}


def write_scorecard_artifacts(
    out_dir: Path,
    catalog_scores: Sequence[CatalogScore] | Sequence[dict[str, Any]],
    stage2_results: Sequence[Stage2ModelResult] | Sequence[dict[str, Any]],
) -> dict[str, Path]:
    if out_dir.exists() and not out_dir.is_dir():
        raise ValueError(f"Scorecard output path is not a directory: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    catalog_payload = {
        "schema_version": SCHEMA_VERSION,
        "scores": [public_payload(item) for item in catalog_scores],
    }
    stage2_payload = {
        "schema_version": SCHEMA_VERSION,
        "results": [public_payload(item) for item in stage2_results],
    }
    _validate_catalog_payload(catalog_payload)
    _validate_stage2_payload(stage2_payload)
    paths = {
        "catalog_scorecard": out_dir / CATALOG_SCORECARD_FILE,
        "stage2_calibration_results": out_dir / STAGE2_RESULTS_FILE,
        "scorecard_summary": out_dir / SCORECARD_SUMMARY_FILE,
    }
    write_json(paths["catalog_scorecard"], catalog_payload)
    write_json(paths["stage2_calibration_results"], stage2_payload)
    paths["scorecard_summary"].write_text(
        build_scorecard_summary(catalog_payload, stage2_payload),
        encoding="utf-8",
    )
    return paths


def read_catalog_scorecard(path: Path) -> dict[str, Any]:
    payload = read_json(path, "Catalog scorecard")
    _validate_catalog_payload(payload)
    return payload


def read_stage2_results(path: Path) -> dict[str, Any]:
    payload = read_json(path, "Stage 2 scorecard results")
    _validate_stage2_payload(payload)
    return payload


def build_scorecard_summary(
    catalog_payload: Mapping[str, Any],
    stage2_payload: Mapping[str, Any],
) -> str:
    catalog = public_payload(catalog_payload)
    stage2 = public_payload(stage2_payload)
    validate_no_secret_fields(catalog)
    validate_no_secret_fields(stage2)
    lines = [
        "# Serverless Model Scorecard Summary",
        "",
        "Catalog scores are predicted from provider metadata.",
        "",
        "## Predicted Catalog Fit",
        "",
        "| Model | Score Type | Total Score | Risk Flags |",
        "|---|---|---:|---|",
    ]
    for row in _rows(catalog.get("scores", [])):
        flags = ", ".join(str(flag) for flag in row.get("risk_flags", []))
        lines.append(
            f"| {row.get('model_id', '')} | {row.get('score_type', '')} | "
            f"{row.get('total_score', '')} | {flags} |"
        )
    lines.extend(
        [
            "",
            "Stage 2 results are measured from direct smoke and WOPR one-turn runs.",
            "",
            "## Measured Stage 2 Operational Fit",
            "",
            "| Model | Status | WOPR One-Turn | Invalid Actions | Retries | Traces |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for row in _rows(stage2.get("results", [])):
        wopr = "yes" if row.get("wopr_one_turn_passed") else "no"
        lines.append(
            f"| {row.get('model_id', '')} | {row.get('status', '')} | {wopr} | "
            f"{row.get('invalid_action_count', '')} | {row.get('retry_count', '')} | "
            f"{row.get('trace_count', '')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _validate_catalog_payload(payload: Any) -> None:
    validate_payload(payload, _CATALOG_FIELDS, "scores", "Catalog scorecard")


def _validate_stage2_payload(payload: Any) -> None:
    validate_payload(
        payload,
        _STAGE2_FIELDS,
        "results",
        "Stage 2 scorecard results",
    )


def _rows(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    rows = [row for row in value if isinstance(row, Mapping)]
    return sorted(rows, key=lambda row: str(row.get("model_id", "")))


__all__ = [
    "CATALOG_SCORECARD_FILE",
    "SCORECARD_SUMMARY_FILE",
    "STAGE2_RESULTS_FILE",
    "build_scorecard_summary",
    "read_catalog_scorecard",
    "read_stage2_results",
    "write_scorecard_artifacts",
]
