"""SiliSocs demo example config tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.llm_harness_batch import load_no_press_llm_batch_config
from nuclear_war_silisocs.demo import run_silisocs_no_press_demo

SCRIPTED_EXAMPLE = Path("docs/examples/silisocs_no_press_scripted_demo.json")
TOGETHER_EXAMPLE = Path("docs/examples/silisocs_no_press_together_demo.json")


def test_scripted_silisocs_demo_example_runs(tmp_path) -> None:
    config = load_no_press_llm_batch_config(
        json.loads(SCRIPTED_EXAMPLE.read_text(encoding="utf-8"))
    )

    result = run_silisocs_no_press_demo(config, tmp_path, scenario_name="example")

    assert result["replay_path"].is_file()
    assert result["trace_path"].is_file()


def test_together_silisocs_demo_example_parses_without_secrets() -> None:
    payload = json.loads(TOGETHER_EXAMPLE.read_text(encoding="utf-8"))
    config = load_no_press_llm_batch_config(payload)
    client = config.seats["player_0"].client

    assert client is not None
    assert client.base_url == "https://api.together.ai/v1"
    assert client.model_env == "WOPR_LLM_MODEL"
    assert client.api_key_env == "TOGETHER_API_KEY"
