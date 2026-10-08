"""Env-gated live Concordia HTTP smoke test."""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

import pytest

# Same guard as test_concordia_native_harness.py: import the real package so
# broken installs are caught, before the project imports, honoring
# WOPR_REQUIRE_CONCORDIA (any non-empty value fails instead of skipping).
# The env-var gate stays separate below so the two skip causes report
# distinct reasons.
try:
    importlib.import_module("concordia")
except ImportError as exc:
    if os.environ.get("WOPR_REQUIRE_CONCORDIA"):
        pytest.fail(
            f"WOPR_REQUIRE_CONCORDIA is set but gdm-concordia is unavailable: {exc}",
            pytrace=False,
        )
    pytest.skip("requires gdm-concordia", allow_module_level=True)

from nuclear_war_concordia.config import load_concordia_no_press_config  # noqa: E402
from nuclear_war_concordia.harness import run_concordia_no_press_game  # noqa: E402
from nuclear_war_env.llm_trace_artifacts import validate_trace_artifact  # noqa: E402


@pytest.mark.skipif(
    not os.environ.get("TOGETHER_API_KEY"),
    reason="requires TOGETHER_API_KEY",
)
def test_live_native_concordia_http_smoke_completes_one_turn() -> None:
    payload = json.loads(
        Path("docs/examples/concordia_no_press_together_demo.json").read_text()
    )
    payload["max_turns"] = 1
    config = load_concordia_no_press_config(payload)

    result = run_concordia_no_press_game(config)

    validate_trace_artifact(result["trace_artifact"], result["replay"])
    assert result["summary"]["trace_count"] >= 1
    assert result["summary"]["fallback_count"] == 0
