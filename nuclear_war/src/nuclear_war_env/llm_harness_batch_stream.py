"""Streaming runner for no-press LLM harness batches.

Writes each game's replay and trace artifacts the moment that game finishes, so
a crash partway through a long batch keeps the completed games plus a
``failure_marker.json`` describing where it stopped, instead of discarding every
finished game (the eager ``run_no_press_llm_batch`` builds everything in memory
first). On success this writes exactly the same ``summary.json`` (byte for byte)
as ``run_no_press_llm_batch`` followed by ``write_no_press_llm_batch``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .llm_harness import run_no_press_llm_game
from .llm_harness_batch import (
    NoPressLLMBatchConfig,
    compact_game,
    game_config,
    validate_batch_config,
)
from .llm_harness_batch_config_snapshot import batch_config_snapshot
from .llm_harness_batch_io import (
    prepare_out_dir,
    summary_payload,
    write_game_artifacts,
    write_summary,
)
from .llm_harness_batch_summary import summarize_no_press_llm_results


def run_no_press_llm_batch_to_dir(
    out_dir: Path,
    config: NoPressLLMBatchConfig,
) -> Path:
    validate_batch_config(config)
    prepare_out_dir(out_dir)
    compact_results: list[dict[str, Any]] = []
    written_results: list[dict[str, Any]] = []
    seat_config: dict[str, str] | None = None
    for index in range(config.runs):
        seed = config.seed_start + index
        try:
            game = run_no_press_llm_game(game_config(config, index))
        except Exception as exc:
            _write_failure_marker(out_dir, config, index, seed, exc, written_results)
            raise ValueError(
                f"LLM experiment aborted at seed {seed} "
                f"({index} of {config.runs} games completed): {exc}"
            ) from exc
        compact = compact_game(game)
        written_results.append(write_game_artifacts(out_dir, game, compact))
        compact_results.append(compact)
        if seat_config is None:
            seat_config = game["seat_config"]
    # validate_batch_config guarantees runs >= 1, so at least one game ran.
    assert seat_config is not None
    result = {
        "mode": "table",
        "players": config.players,
        "seed_start": config.seed_start,
        "runs": config.runs,
        "max_turns": config.max_turns,
        "config": batch_config_snapshot(config),
        "seat_config": seat_config,
        "summary": summarize_no_press_llm_results(compact_results, seat_config),
    }
    return write_summary(out_dir, summary_payload(result, written_results))


def _write_failure_marker(
    out_dir: Path,
    config: NoPressLLMBatchConfig,
    completed_runs: int,
    failed_seed: int,
    exc: Exception,
    written_results: list[dict[str, Any]],
) -> Path:
    marker = {
        "status": "aborted",
        "requested_runs": config.runs,
        "completed_runs": completed_runs,
        "failed_seed": failed_seed,
        "error": str(exc),
        "results": written_results,
    }
    marker_path = out_dir / "failure_marker.json"
    marker_path.write_text(
        json.dumps(marker, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return marker_path


__all__ = ["run_no_press_llm_batch_to_dir"]
