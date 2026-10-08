"""Artifact writing for no-press LLM harness batches."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .llm_harness_batch_validation import validate_no_press_llm_batch
from .llm_trace_artifacts import write_trace_artifact
from .replay import write_replay


def write_no_press_llm_batch(out_dir: Path, result: dict[str, Any]) -> Path:
    prepare_out_dir(out_dir)
    written_results = [
        write_game_artifacts(out_dir, game, compact)
        for game, compact in zip(result["games"], result["results"], strict=True)
    ]
    return write_summary(out_dir, summary_payload(result, written_results))


def read_no_press_llm_batch(summary_path: Path) -> dict[str, Any]:
    if not summary_path.exists():
        raise ValueError(f"LLM experiment summary not found: {summary_path}")
    if not summary_path.is_file():
        raise ValueError(f"LLM experiment summary path is not a file: {summary_path}")
    try:
        payload = json.loads(
            summary_path.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(
            f"LLM experiment summary is not valid JSON: {summary_path}"
        ) from exc
    validate_no_press_llm_batch(payload, summary_path.parent)
    return payload


def prepare_out_dir(out_dir: Path) -> None:
    if out_dir.exists() and not out_dir.is_dir():
        raise ValueError(f"LLM experiment output path is not a directory: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)


def write_game_artifacts(
    out_dir: Path,
    game: dict[str, Any],
    compact: dict[str, Any],
) -> dict[str, Any]:
    seed = int(game["replay"]["seed"])
    replay_path = out_dir / f"seed-{seed}.replay.json"
    write_replay(replay_path, game["replay"])
    trace_path = write_trace_artifact(
        replay_path,
        game["replay"],
        game["trace_artifact"]["traces"],
    )
    return {
        **compact,
        "replay_path": replay_path.name,
        "trace_path": trace_path.name,
    }


def write_summary(out_dir: Path, payload: dict[str, Any]) -> Path:
    summary_path = out_dir / "summary.json"
    summary_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return summary_path


def summary_payload(
    result: dict[str, Any],
    written_results: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "mode": result["mode"],
        "players": result["players"],
        "seed_start": result["seed_start"],
        "runs": result["runs"],
        "max_turns": result["max_turns"],
        "config": result["config"],
        "seat_config": result["seat_config"],
        "results": written_results,
        "summary": result["summary"],
    }


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


__all__ = [
    "prepare_out_dir",
    "read_no_press_llm_batch",
    "summary_payload",
    "validate_no_press_llm_batch",
    "write_game_artifacts",
    "write_no_press_llm_batch",
    "write_summary",
]
