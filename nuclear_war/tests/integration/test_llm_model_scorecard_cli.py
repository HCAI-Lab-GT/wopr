"""CLI tests for serverless model scorecard artifacts."""

from __future__ import annotations

import json

import pytest

from nuclear_war_env.cli import main


def test_cli_scorecard_catalog_writes_predicted_artifacts(tmp_path, capsys) -> None:
    catalog_path = _write_catalog(tmp_path)
    out_dir = tmp_path / "scorecard"

    code = main(_args(catalog_path, out_dir, "catalog"))

    captured = capsys.readouterr()
    assert code == 0
    paths = json.loads(captured.out)
    catalog = json.loads((out_dir / "catalog_scorecard.json").read_text())
    stage2 = json.loads((out_dir / "stage2_calibration_results.json").read_text())
    assert paths == _expected_paths(out_dir)
    assert [row["model_id"] for row in catalog["scores"]] == [
        "demo/low-cost",
        "demo/context",
    ]
    assert {row["score_type"] for row in catalog["scores"]} == {"predicted"}
    assert stage2["results"] == []
    assert (out_dir / "scorecard_summary.md").is_file()


def test_cli_scorecard_stage2_fake_writes_measured_results(tmp_path, capsys) -> None:
    catalog_path = _write_catalog(tmp_path)
    out_dir = tmp_path / "scorecard"

    code = main(
        _args(catalog_path, out_dir, "stage2")
        + [
            "--provider",
            "fake",
            "--model-limit",
            "1",
            "--seed-start",
            "13",
            "--max-turns",
            "1",
        ]
    )

    captured = capsys.readouterr()
    assert code == 0
    catalog = json.loads((out_dir / "catalog_scorecard.json").read_text())
    stage2 = json.loads((out_dir / "stage2_calibration_results.json").read_text())
    result = stage2["results"][0]
    assert json.loads(captured.out) == _expected_paths(out_dir)
    assert [row["model_id"] for row in catalog["scores"]] == ["demo/low-cost"]
    assert result["model_id"] == "demo/low-cost"
    assert result["status"] == "passed"
    assert result["direct_smoke_passed"] is True
    assert result["wopr_one_turn_passed"] is True
    assert result["trace_count"] > 0
    assert result["error_type"] is None


@pytest.mark.parametrize("payload", [None, {}])
def test_cli_model_scorecard_catalog_input_errors_return_code_2(
    tmp_path,
    capsys,
    payload,
) -> None:
    catalog_path = tmp_path / "missing.json"
    if payload is not None:
        catalog_path.write_text(json.dumps(payload), encoding="utf-8")
    out_dir = tmp_path / "scorecard"

    code = main(_args(catalog_path, out_dir, "catalog"))

    captured = capsys.readouterr()
    assert code == 2
    assert "nuclear-war: error:" in captured.err
    assert not out_dir.exists()


@pytest.mark.parametrize(
    ("extra_args", "message"),
    [
        (["--max-tokens", "64"], "--max-tokens is not supported"),
        (["--reasoning-effort", "low"], "--reasoning-effort is not supported"),
        (["--max-models-cost-usd", "0.01"], "--max-models-cost-usd is not supported"),
    ],
)
def test_cli_model_scorecard_stage2_fake_rejects_unsupported_controls(
    tmp_path,
    capsys,
    extra_args,
    message,
) -> None:
    catalog_path = _write_catalog(tmp_path)
    out_dir = tmp_path / "scorecard"

    code = main(
        _args(catalog_path, out_dir, "stage2")
        + ["--provider", "fake", "--model-limit", "1"]
        + extra_args
    )

    captured = capsys.readouterr()
    assert code == 2
    assert message in captured.err
    assert not out_dir.exists()


def _write_catalog(tmp_path):
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(_catalog_payload()), encoding="utf-8")
    return catalog_path


def _args(catalog_path, out_dir, stage: str) -> list[str]:
    return [
        "llm-model-scorecard",
        "--catalog",
        str(catalog_path),
        "--out",
        str(out_dir),
        "--stage",
        stage,
    ]


def _catalog_payload() -> dict[str, object]:
    return {
        "chat": [
            {"id": "demo/low-cost", "name": "Low Cost"},
            {"id": "demo/context", "name": "Context"},
        ]
    }


def _expected_paths(out_dir) -> dict[str, str]:
    return {
        "catalog_scorecard": str(out_dir / "catalog_scorecard.json"),
        "scorecard_summary": str(out_dir / "scorecard_summary.md"),
        "stage2_calibration_results": str(out_dir / "stage2_calibration_results.json"),
    }
