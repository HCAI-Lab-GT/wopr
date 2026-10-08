"""Artifact writer for Concordia no-press demo runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from nuclear_war_env.replay import write_replay


def write_concordia_no_press_artifacts(
    out_dir: Path,
    result: dict[str, Any],
) -> dict[str, Path]:
    wopr_dir = out_dir / "wopr"
    concordia_dir = out_dir / "concordia"
    wopr_dir.mkdir(parents=True, exist_ok=True)
    concordia_dir.mkdir(parents=True, exist_ok=True)

    replay_path = wopr_dir / "replay.json"
    trace_path = wopr_dir / "traces.json"
    c2_path = concordia_dir / "c2_deliberations.json"
    summary_path = concordia_dir / "run_summary.json"
    config_path = concordia_dir / "config_snapshot.json"
    agent_metadata_path = concordia_dir / "agent_metadata.json"
    runtime_path = concordia_dir / "runtime_status.json"

    write_replay(replay_path, result["replay"])
    _write_json(trace_path, result["trace_artifact"])
    _write_json(c2_path, result["c2_artifact"])
    _write_json(summary_path, result["summary"])
    _write_json(config_path, result["config_snapshot"])
    _write_json(agent_metadata_path, result["agent_metadata"])
    _write_json(runtime_path, result["runtime"])

    if "press_artifact" in result:
        press_path = concordia_dir / "press_traces.json"
        _write_json(press_path, result["press_artifact"])

    return {
        "replay_path": replay_path,
        "trace_path": trace_path,
        "c2_path": c2_path,
        "summary_path": summary_path,
        "config_path": config_path,
        "agent_metadata_path": agent_metadata_path,
        "runtime_path": runtime_path,
        **({"press_path": press_path} if "press_artifact" in result else {}),
    }


def write_concordia_failure_artifact(
    out_dir: Path,
    snapshot: dict[str, Any],
) -> dict[str, Path]:
    concordia_dir = out_dir / "concordia"
    concordia_dir.mkdir(parents=True, exist_ok=True)
    failure_path = concordia_dir / "failure_snapshot.json"
    _write_json(failure_path, snapshot)
    return {"failure_snapshot_path": failure_path}


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


__all__ = ["write_concordia_failure_artifact", "write_concordia_no_press_artifacts"]
