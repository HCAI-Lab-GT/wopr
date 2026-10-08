"""CLI validation tests for model scorecard controls."""

from __future__ import annotations

import json

import pytest

from nuclear_war_env.cli import main


@pytest.mark.parametrize("cost_cap", ["-1", "nan", "inf"])
def test_cli_scorecard_rejects_invalid_cost_cap_before_artifacts(
    tmp_path,
    capsys,
    cost_cap,
) -> None:
    catalog_path = _write_catalog(tmp_path)
    out_dir = tmp_path / "scorecard"

    code = main(
        _args(catalog_path, out_dir, "catalog") + ["--max-models-cost-usd", cost_cap]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "--max-models-cost-usd must be positive" in captured.err
    assert not out_dir.exists()


def test_cli_stage2_together_requires_cost_cap_before_artifacts(
    tmp_path,
    capsys,
) -> None:
    catalog_path = _write_catalog(tmp_path)
    out_dir = tmp_path / "scorecard"

    code = main(
        _args(catalog_path, out_dir, "stage2")
        + ["--provider", "together", "--model-limit", "1"]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "--max-models-cost-usd is required" in captured.err
    assert not out_dir.exists()


@pytest.mark.parametrize("cost_cap", ["0", "-0.25"])
def test_cli_stage2_together_rejects_nonpositive_cost_cap_before_artifacts(
    tmp_path,
    capsys,
    cost_cap,
) -> None:
    catalog_path = _write_catalog(tmp_path)
    out_dir = tmp_path / "scorecard"

    code = main(
        _args(catalog_path, out_dir, "stage2")
        + [
            "--provider",
            "together",
            "--model-limit",
            "1",
            "--max-models-cost-usd",
            cost_cap,
        ]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "--max-models-cost-usd must be positive" in captured.err
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
    return {"chat": [{"id": "demo/low-cost", "name": "Low Cost"}]}
