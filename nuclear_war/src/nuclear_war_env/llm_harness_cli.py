"""CLI helpers for deterministic no-press LLM harness batches."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from nuclear_war_concordia.artifacts import (
    write_concordia_failure_artifact,
    write_concordia_no_press_artifacts,
)
from nuclear_war_concordia.config import load_concordia_no_press_config
from nuclear_war_concordia.failure import ConcordiaRunFailure
from nuclear_war_concordia.harness import run_concordia_no_press_game
from nuclear_war_silisocs.demo import run_silisocs_no_press_demo

from .llm_harness_batch import load_no_press_llm_batch_config
from .llm_harness_batch_io import read_no_press_llm_batch
from .llm_harness_batch_stream import run_no_press_llm_batch_to_dir
from .llm_preflight import run_llm_preflight


def add_llm_harness_parser(subparsers: argparse._SubParsersAction) -> None:
    llm_experiment = subparsers.add_parser("llm-experiment")
    llm_experiment.add_argument("--config", required=True)
    llm_experiment.add_argument("--out-dir", required=True)
    llm_preflight = subparsers.add_parser("llm-preflight")
    llm_preflight.add_argument("--config", required=True)
    llm_summarize = subparsers.add_parser("llm-summarize")
    llm_summarize.add_argument("path")
    silisocs_demo = subparsers.add_parser("silisocs-demo")
    silisocs_demo.add_argument("--config", required=True)
    silisocs_demo.add_argument("--out-dir", required=True)
    silisocs_demo.add_argument(
        "--scenario-name",
        default="nuclear_war_no_press",
    )
    concordia_demo = subparsers.add_parser("concordia-demo")
    concordia_demo.add_argument("--config", required=True)
    concordia_demo.add_argument("--out-dir", required=True)


def run_llm_harness_command(args: argparse.Namespace) -> int | None:
    if args.command == "llm-experiment":
        config = load_no_press_llm_batch_config(_read_json(Path(args.config)))
        # Stream games to disk as they complete so a mid-batch crash keeps the
        # finished games plus a failure marker instead of discarding everything.
        summary_path = run_no_press_llm_batch_to_dir(Path(args.out_dir), config)
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        print(json.dumps(summary["summary"], indent=2, sort_keys=True))
        return 0
    if args.command == "llm-preflight":
        report = run_llm_preflight(_read_json(Path(args.config)))
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if args.command == "llm-summarize":
        payload = read_no_press_llm_batch(Path(args.path))
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
        return 0
    if args.command == "silisocs-demo":
        config = load_no_press_llm_batch_config(_read_json(Path(args.config)))
        result = run_silisocs_no_press_demo(
            config,
            Path(args.out_dir),
            scenario_name=args.scenario_name,
        )
        print(json.dumps(_path_payload(result), indent=2, sort_keys=True))
        return 0
    if args.command == "concordia-demo":
        config = load_concordia_no_press_config(_read_json(Path(args.config)))
        try:
            result = run_concordia_no_press_game(config)
        except ConcordiaRunFailure as exc:
            paths = write_concordia_failure_artifact(Path(args.out_dir), exc.snapshot)
            print(json.dumps(_path_payload(paths), indent=2, sort_keys=True))
            raise ValueError(str(exc)) from exc
        paths = write_concordia_no_press_artifacts(Path(args.out_dir), result)
        print(json.dumps(_path_payload(paths), indent=2, sort_keys=True))
        return 0
    return None


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read JSON config: {path}") from exc


def _path_payload(payload: dict[str, Path]) -> dict[str, str]:
    return {key: str(value) for key, value in payload.items()}


__all__ = ["add_llm_harness_parser", "run_llm_harness_command"]
