"""CLI helpers for serverless model scorecards."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from math import isfinite
from pathlib import Path

from nuclear_war_agents.llm_http_client import HTTPClientConfig, LLMHttpClient

from .llm_model_scorecard_catalog import (
    ModelCatalogRow,
    load_catalog_rows,
    score_catalog_rows,
)
from .llm_model_scorecard_fake_client import ScorecardFakeClient
from .llm_model_scorecard_io import write_scorecard_artifacts
from .llm_model_scorecard_stage2 import Stage2Config, run_stage2_model
from .llm_model_scorecard_stage2_support import Stage2ModelResult


def add_model_scorecard_parser(subparsers: argparse._SubParsersAction) -> None:
    scorecard = subparsers.add_parser("llm-model-scorecard")
    scorecard.add_argument("--catalog", required=True)
    scorecard.add_argument("--stage", choices=["catalog", "stage2"], required=True)
    scorecard.add_argument("--model-limit", type=int)
    scorecard.add_argument("--max-models-cost-usd", type=float)
    scorecard.add_argument("--seed-start", type=int, default=101)
    scorecard.add_argument("--max-turns", type=int, default=1)
    scorecard.add_argument("--max-tokens", type=int)
    scorecard.add_argument("--reasoning-effort", choices=["low", "medium", "high"])
    scorecard.add_argument("--disable-reasoning", action="store_true")
    scorecard.add_argument("--stream", action="store_true")
    scorecard.add_argument("--provider")
    scorecard.add_argument("--out", required=True)


def run_model_scorecard_command(args: argparse.Namespace) -> int | None:
    if args.command != "llm-model-scorecard":
        return None
    _validate_args(args)
    rows = _limited_rows(_load_catalog_rows(Path(args.catalog)), args.model_limit)
    catalog_scores = score_catalog_rows(rows)
    stage2_results = _stage2_results(args, rows) if args.stage == "stage2" else []
    paths = write_scorecard_artifacts(Path(args.out), catalog_scores, stage2_results)
    payload = {key: str(value) for key, value in paths.items()}
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _stage2_results(
    args: argparse.Namespace,
    rows: Sequence[ModelCatalogRow],
) -> list[Stage2ModelResult]:
    client_factory = _stage2_client_factory(args)
    results = []
    for index, row in enumerate(rows):
        config = Stage2Config(
            seed=args.seed_start + index,
            max_turns=args.max_turns,
        )
        results.append(run_stage2_model(config, row.model_id, client_factory))
    return results


def _limited_rows(
    rows: Sequence[ModelCatalogRow],
    model_limit: int | None,
) -> list[ModelCatalogRow]:
    selected = list(rows)
    if model_limit is None:
        return selected
    if model_limit < 1:
        raise ValueError("--model-limit must be positive")
    return selected[:model_limit]


def _validate_args(args: argparse.Namespace) -> None:
    if args.max_turns < 1:
        raise ValueError("--max-turns must be positive")
    if args.max_tokens is not None and args.max_tokens < 1:
        raise ValueError("--max-tokens must be positive")
    if args.max_models_cost_usd is not None and (
        args.max_models_cost_usd <= 0 or not isfinite(args.max_models_cost_usd)
    ):
        raise ValueError("--max-models-cost-usd must be positive and finite")
    if args.stage == "stage2" and args.provider == "together":
        _validate_provider_stage2_args(args)


def _stage2_client_factory(args: argparse.Namespace):
    if args.provider == "fake":
        _validate_fake_stage2_args(args)
        return _fake_client
    if args.provider == "together":
        _validate_provider_stage2_args(args)
        return _together_client_factory(args)
    raise ValueError("Stage 2 supports --provider fake or --provider together")


def _validate_fake_stage2_args(args: argparse.Namespace) -> None:
    if args.max_tokens is not None:
        raise ValueError("--max-tokens is not supported for fake Stage 2")
    if args.reasoning_effort is not None:
        raise ValueError("--reasoning-effort is not supported for fake Stage 2")
    if args.disable_reasoning:
        raise ValueError("--disable-reasoning is not supported for fake Stage 2")
    if args.stream:
        raise ValueError("--stream is not supported for fake Stage 2")
    if args.max_models_cost_usd is not None:
        raise ValueError("--max-models-cost-usd is not supported for fake Stage 2")


def _validate_provider_stage2_args(args: argparse.Namespace) -> None:
    if args.max_models_cost_usd is None:
        raise ValueError("--max-models-cost-usd is required for real Stage 2")


def _load_catalog_rows(path: Path) -> list[ModelCatalogRow]:
    try:
        return load_catalog_rows(path)
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Could not load model catalog: {path}") from exc


def _together_client_factory(args: argparse.Namespace):
    default_max_tokens = HTTPClientConfig().max_tokens
    max_tokens = args.max_tokens if args.max_tokens is not None else default_max_tokens
    return lambda model_id: LLMHttpClient(
        HTTPClientConfig(
            provider="together",
            model=model_id,
            max_tokens=max_tokens,
            reasoning_effort=args.reasoning_effort,
            reasoning_enabled=False if args.disable_reasoning else None,
            stream=args.stream,
        )
    )


def _fake_client(_model_id: str) -> ScorecardFakeClient:
    return ScorecardFakeClient()


__all__ = ["add_model_scorecard_parser", "run_model_scorecard_command"]
