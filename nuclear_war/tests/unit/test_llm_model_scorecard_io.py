"""Scorecard artifact IO tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_env.llm_model_scorecard_catalog import CatalogScore
from nuclear_war_env.llm_model_scorecard_io import (
    build_scorecard_summary,
    read_catalog_scorecard,
    read_stage2_results,
    write_scorecard_artifacts,
)
from nuclear_war_env.llm_model_scorecard_stage2 import Stage2ModelResult


def test_write_scorecard_artifacts_round_trips_fixed_files(tmp_path) -> None:
    paths = write_scorecard_artifacts(
        tmp_path,
        [_catalog_score()],
        [_stage2_result()],
    )

    catalog_payload = read_catalog_scorecard(paths["catalog_scorecard"])
    stage2_payload = read_stage2_results(paths["stage2_calibration_results"])
    summary = paths["scorecard_summary"].read_text(encoding="utf-8")

    assert paths == {
        "catalog_scorecard": tmp_path / "catalog_scorecard.json",
        "stage2_calibration_results": tmp_path / "stage2_calibration_results.json",
        "scorecard_summary": tmp_path / "scorecard_summary.md",
    }
    assert catalog_payload["scores"][0]["score_type"] == "predicted"
    assert stage2_payload["results"][0]["status"] == "passed"
    assert "## Predicted Catalog Fit" in summary
    assert "## Measured Stage 2 Operational Fit" in summary
    assert summary.index("## Predicted Catalog Fit") < summary.index(
        "## Measured Stage 2 Operational Fit"
    )


def test_write_scorecard_artifacts_uses_sorted_strict_json(tmp_path) -> None:
    paths = write_scorecard_artifacts(
        tmp_path,
        [_catalog_score()],
        [_stage2_result()],
    )

    catalog_text = paths["catalog_scorecard"].read_text(encoding="utf-8")
    assert catalog_text.endswith("\n")
    assert catalog_text.index('"context_score"') < catalog_text.index('"cost_score"')
    assert json.loads(catalog_text)["scores"][0]["risk_flags"] == [
        "missing_function_calling"
    ]


def test_write_scorecard_artifacts_allows_generic_provider_usage_tokens(
    tmp_path,
) -> None:
    paths = write_scorecard_artifacts(
        tmp_path,
        [_catalog_score()],
        [_stage2_result(provider_usage={"tokens": 42})],
    )

    payload = read_stage2_results(paths["stage2_calibration_results"])

    assert payload["results"][0]["provider_usage"] == {"tokens": 42}


@pytest.mark.parametrize(
    "secret_key",
    [
        "api_key",
        "apiKey",
        "authorization",
        "raw_headers",
        "rawHeaders",
        "access_token",
        "accessToken",
        "refresh_token",
        "bearer_token",
        "provider_account_id",
        "providerAccountIdentifier",
    ],
)
def test_write_scorecard_artifacts_rejects_secret_bearing_keys(
    tmp_path,
    secret_key: str,
) -> None:
    with pytest.raises(ValueError, match="secret-bearing field"):
        write_scorecard_artifacts(
            tmp_path,
            [{"model_id": "demo/model", secret_key: "not-written"}],
            [],
        )


def test_build_scorecard_summary_separates_prediction_from_measurement() -> None:
    summary = build_scorecard_summary(
        {"scores": [_catalog_score().__dict__]},
        {"results": [_stage2_result().__dict__]},
    )

    assert "| demo/model | predicted | 42.5 |" in summary
    assert "| demo/model | passed | yes | 0 | 0 |" in summary
    assert "Catalog scores are predicted from provider metadata." in summary
    assert (
        "Stage 2 results are measured from direct smoke and WOPR one-turn runs."
        in summary
    )


def _catalog_score() -> CatalogScore:
    return CatalogScore(
        model_id="demo/model",
        score_type="predicted",
        total_score=42.5,
        cost_score=20.0,
        context_score=10.0,
        interface_score=12.5,
        risk_flags=("missing_function_calling",),
    )


def _stage2_result(
    provider_usage: dict[str, int | float] | None = None,
) -> Stage2ModelResult:
    return Stage2ModelResult(
        model_id="demo/model",
        status="passed",
        direct_smoke_passed=True,
        wopr_one_turn_passed=True,
        trace_count=3,
        invalid_action_count=0,
        retry_count=0,
        selected_action_ids=("player_0:draw",),
        provider_usage=(
            {"total_tokens": 20} if provider_usage is None else provider_usage
        ),
        provider_latency_ms=19,
        error_type=None,
        error_message=None,
    )
