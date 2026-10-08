"""LLM model scorecard catalog tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nuclear_war_env.llm_model_scorecard_catalog import (
    ModelCatalogRow,
    load_catalog_rows,
    score_catalog_row,
    score_catalog_rows,
)

CATALOG_PATH = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "llm_model_calibration"
    / "data"
    / "serverless_catalog_2026-07-05.json"
)


def test_load_catalog_rows_loads_23_chat_models() -> None:
    rows = load_catalog_rows(CATALOG_PATH)

    assert len(rows) == 23
    assert rows[0].model_id == "MiniMaxAI/MiniMax-M3"
    assert rows[-1].model_id == "zai-org/GLM-5.1"


def test_score_catalog_row_prefers_gpt_oss_20b_over_llama_3_8b_lite() -> None:
    rows = load_catalog_rows(CATALOG_PATH)
    scores = {
        row.model_id: score_catalog_row(row)
        for row in rows
        if row.model_id
        in {
            "openai/gpt-oss-20b",
            "meta-llama/Meta-Llama-3-8B-Instruct-Lite",
        }
    }

    assert (
        scores["openai/gpt-oss-20b"].total_score
        > scores["meta-llama/Meta-Llama-3-8B-Instruct-Lite"].total_score
    )


def test_score_catalog_rows_are_predicted() -> None:
    rows = load_catalog_rows(CATALOG_PATH)

    scores = score_catalog_rows(rows)

    assert {score.score_type for score in scores} == {"predicted"}


def test_cached_input_price_zero_beats_missing_cached_input_price() -> None:
    base_row = ModelCatalogRow(
        model_id="test/model",
        name="Test Model",
        context=128000,
        input_price=0.2,
        cached_input_price=None,
        output_price=0.2,
        quantization=None,
        function_calling="yes",
        structured_outputs="yes",
    )

    zero_cached_row = ModelCatalogRow(
        model_id="test/model",
        name="Test Model",
        context=128000,
        input_price=0.2,
        cached_input_price=0.0,
        output_price=0.2,
        quantization=None,
        function_calling="yes",
        structured_outputs="yes",
    )

    assert (
        score_catalog_row(zero_cached_row).cost_score
        > score_catalog_row(base_row).cost_score
    )


@pytest.mark.parametrize("field_name", ["context", "input"])
def test_load_catalog_rows_rejects_unsupported_numeric_values(
    tmp_path: Path, field_name: str
) -> None:
    row: dict[str, object] = {
        "id": "test/model",
        "name": "Test Model",
        "context": 128000,
        "input": 0.2,
        "cached_input": 0.0,
        "output": 0.2,
        "quantization": None,
        "function_calling": "yes",
        "structured_outputs": "yes",
    }
    row[field_name] = {"value": 1}
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps({"chat": [row]}), encoding="utf-8")

    with pytest.raises(ValueError, match=f"Catalog numeric field {field_name}"):
        load_catalog_rows(catalog_path)
