"""Shared helpers for the bounded authority smoke tests."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from nuclear_war_agents.llm_http_transport import HTTPResponse, HTTPTransport
from nuclear_war_concordia.c2_artifacts import validate_c2_artifact
from nuclear_war_concordia.press_artifacts import validate_press_artifact
from nuclear_war_env.llm_trace_artifacts import (
    read_trace_artifact,
    validate_trace_artifact,
)
from nuclear_war_env.replay import read_replay


def _budgeted_transport(
    delegate: HTTPTransport,
    budget: int,
) -> tuple[HTTPTransport, Callable[[], int]]:
    calls = 0

    def transport(
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout: int,
    ) -> HTTPResponse:
        nonlocal calls
        if calls >= budget:
            raise RuntimeError("provider request budget exceeded")
        calls += 1
        return delegate(url, headers, body, timeout)

    return transport, lambda: calls


def _reload_authority_artifacts(paths: dict[str, Path]) -> dict[str, Any]:
    replay = read_replay(paths["replay_path"])
    trace = read_trace_artifact(paths["trace_path"], replay)
    c2 = json.loads(paths["c2_path"].read_text(encoding="utf-8"))
    press = json.loads(paths["press_path"].read_text(encoding="utf-8"))
    config = json.loads(paths["config_path"].read_text(encoding="utf-8"))
    metadata = json.loads(paths["agent_metadata_path"].read_text(encoding="utf-8"))
    runtime = json.loads(paths["runtime_path"].read_text(encoding="utf-8"))
    summary = json.loads(paths["summary_path"].read_text(encoding="utf-8"))
    validate_trace_artifact(trace, replay)
    validate_c2_artifact(c2, replay)
    validate_press_artifact(press, replay)
    return {
        "replay": replay,
        "trace_artifact": trace,
        "c2_artifact": c2,
        "press_artifact": press,
        "config_snapshot": config,
        "agent_metadata": metadata,
        "runtime": runtime,
        "summary": summary,
    }


def _assert_authority_artifacts(
    result: dict[str, Any],
    paths: dict[str, Path],
    written: dict[str, Any],
    request_count: int,
    request_budget: int,
) -> None:
    assert result["summary"]["fallback_count"] == 0
    assert result["c2_artifact"]["deliberations"]
    assert result["press_artifact"]["messages"]
    assert set(paths) == {
        "replay_path",
        "trace_path",
        "c2_path",
        "summary_path",
        "config_path",
        "agent_metadata_path",
        "runtime_path",
        "press_path",
    }
    assert all(path.exists() and path.stat().st_size > 0 for path in paths.values())
    _assert_written_payloads(result, written)
    _assert_written_metadata(written)
    assert 0 < request_count <= request_budget


def _assert_written_payloads(
    result: dict[str, Any],
    written: dict[str, Any],
) -> None:
    for key in (
        "replay",
        "trace_artifact",
        "c2_artifact",
        "press_artifact",
        "config_snapshot",
        "agent_metadata",
        "runtime",
        "summary",
    ):
        assert written[key] == result[key]


def _assert_written_metadata(written: dict[str, Any]) -> None:
    config = written["config_snapshot"]
    metadata = written["agent_metadata"]
    runtime = written["runtime"]
    summary = written["summary"]
    assert config["seats"]["player_0"]["authority"]["members"]
    assert metadata["player_0"]["client"]["api_key_env"] == "TOGETHER_API_KEY"
    assert runtime["runtime_path"] == "concordia_style_fallback"
    assert summary["fallback_count"] == 0
    assert summary["channel_metrics"]["c2"]["trace_count"] >= 3
    assert summary["channel_metrics"]["press"]["trace_count"] > 0
    assert "TOGETHER_API_KEY" in json.dumps(config)
