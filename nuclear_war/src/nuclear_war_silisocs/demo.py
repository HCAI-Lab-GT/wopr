"""SiliSocs-style demo runner for WOPR Nuclear War experiments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nuclear_war_env.llm_harness_batch import (
    NoPressLLMBatchConfig,
    run_no_press_llm_batch,
)
from nuclear_war_env.llm_harness_batch_config_snapshot import batch_config_snapshot
from nuclear_war_env.llm_trace_artifacts import build_trace_artifact
from nuclear_war_env.replay import write_replay

_RUNTIME_CONTRACTS = {
    "agent": "silisocs.agents.base_agent.Agent",
    "action_spec": "silisocs.runtime.types.ActionSpec",
    "action_output": "silisocs.runtime.types.ActionOutput",
    "backend": "silisocs.environments.backends.base.BackendApp",
}


def run_silisocs_no_press_demo(
    config: NoPressLLMBatchConfig,
    out_dir: Path,
    *,
    scenario_name: str,
) -> dict[str, Path]:
    if config.runs != 1:
        raise ValueError("SiliSocs demo runner requires exactly one run")
    result = run_no_press_llm_batch(config)
    game = result["games"][0]
    wopr_dir = out_dir / "wopr"
    silisocs_dir = out_dir / "silisocs"
    wopr_dir.mkdir(parents=True, exist_ok=True)
    silisocs_dir.mkdir(parents=True, exist_ok=True)
    replay_path = wopr_dir / "replay.json"
    trace_path = wopr_dir / "traces.json"
    summary_path = wopr_dir / "summary.json"
    config_path = silisocs_dir / "config_snapshot.json"
    telemetry_path = silisocs_dir / "telemetry.json"
    write_replay(replay_path, game["replay"])
    _write_json(trace_path, _trace_payload(game))
    _write_json(summary_path, game["summary"])
    _write_json(config_path, batch_config_snapshot(config))
    _write_json(telemetry_path, _telemetry(config, scenario_name))
    _write_readme(out_dir, scenario_name)
    return {
        "replay_path": replay_path,
        "trace_path": trace_path,
        "summary_path": summary_path,
        "config_snapshot_path": config_path,
        "telemetry_path": telemetry_path,
    }


def _trace_payload(game: dict[str, Any]) -> dict[str, Any]:
    return build_trace_artifact(
        game["replay"],
        game["trace_artifact"]["traces"],
    )


def _telemetry(
    config: NoPressLLMBatchConfig,
    scenario_name: str,
) -> dict[str, Any]:
    return {
        "adapter": "wopr_silisocs",
        "scenario_name": scenario_name,
        "runs": config.runs,
        "seed_start": config.seed_start,
        "players": config.players,
        "max_turns": config.max_turns,
        "runtime_contracts": dict(_RUNTIME_CONTRACTS),
        "artifacts": {
            "replay": "wopr/replay.json",
            "traces": "wopr/traces.json",
            "summary": "wopr/summary.json",
        },
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_readme(out_dir: Path, scenario_name: str) -> None:
    body = "\n".join(
        [
            f"# {scenario_name}",
            "",
            "This directory contains a SiliSocs-style WOPR Nuclear War demo run.",
            "",
            "- `wopr/replay.json`: WOPR replay payload.",
            "- `wopr/traces.json`: LLM decision trace sidecar.",
            "- `wopr/summary.json`: compact game summary.",
            "- `silisocs/config_snapshot.json`: demo config snapshot.",
            "- `silisocs/telemetry.json`: adapter and runtime-contract metadata.",
            "",
        ]
    )
    (out_dir / "README.md").write_text(body, encoding="utf-8")


__all__ = ["run_silisocs_no_press_demo"]
