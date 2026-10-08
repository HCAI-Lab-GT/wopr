"""Checked-in pilot experiment configs must load and dry-run offline.

These tests keep ``docs/examples/pilot_no_press_llm_http.json`` and
``docs/examples/pilot_press_light_concordia.json`` from rotting silently:
both are parsed by their real parsers exactly as checked in, and offline
variants (HTTP seats swapped for first-legal fakes at load time) play one
full game each with validated artifacts. No network, no API keys.
"""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_concordia.config import load_concordia_no_press_config
from nuclear_war_concordia.harness import run_concordia_no_press_game
from nuclear_war_env.llm_harness_batch import (
    load_no_press_llm_batch_config,
    run_no_press_llm_batch,
)
from nuclear_war_env.llm_harness_batch_io import (
    read_no_press_llm_batch,
    write_no_press_llm_batch,
)
from nuclear_war_env.llm_trace_artifacts import validate_trace_artifact

NO_PRESS_PILOT = Path("docs/examples/pilot_no_press_llm_http.json")
PRESS_LIGHT_PILOT = Path("docs/examples/pilot_press_light_concordia.json")


def test_pilot_no_press_llm_http_config_loads_as_checked_in() -> None:
    config = load_no_press_llm_batch_config(
        json.loads(NO_PRESS_PILOT.read_text(encoding="utf-8"))
    )

    assert config.players == 4
    assert config.runs == 10
    assert config.max_turns == 40
    seats = {player_id: seat.agent for player_id, seat in config.seats.items()}
    assert seats == {
        "player_0": "llm_http",
        "player_1": "random",
        "player_2": "heuristic",
        "player_3": "decision_heuristic",
    }
    client = config.seats["player_0"].client
    assert client is not None
    # Endpoint settings are env-var driven; the file must hold no secrets.
    assert client.base_url is None and client.base_url_env == "WOPR_LLM_BASE_URL"
    assert client.model is None and client.model_env == "WOPR_LLM_MODEL"
    assert client.api_key_env == "TOGETHER_API_KEY"


def test_pilot_no_press_offline_variant_plays_one_validated_game(tmp_path) -> None:
    payload = json.loads(NO_PRESS_PILOT.read_text(encoding="utf-8"))
    payload["runs"] = 1
    payload["seats"]["player_0"] = {
        "agent": "llm_first_legal",
        "max_retries": payload["seats"]["player_0"]["max_retries"],
        "fallback": payload["seats"]["player_0"]["fallback"],
    }
    config = load_no_press_llm_batch_config(payload)

    result = run_no_press_llm_batch(config)
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)
    validated = read_no_press_llm_batch(summary_path)

    assert validated["runs"] == 1
    assert validated["max_turns"] == 40
    assert validated["summary"]["total_trace_count"] >= 1
    assert (summary_path.parent / "seed-101.replay.json").is_file()
    assert (summary_path.parent / "seed-101.replay.traces.json").is_file()


def test_pilot_press_light_concordia_config_loads_as_checked_in() -> None:
    config = load_concordia_no_press_config(
        json.loads(PRESS_LIGHT_PILOT.read_text(encoding="utf-8"))
    )

    assert config.players == 4
    assert config.max_turns == 40
    assert config.press.mode == "press_light"
    assert config.press.enabled is True
    assert all(seat.agent == "concordia_http" for seat in config.seats.values())
    for seat in config.seats.values():
        assert seat.client is not None
        assert seat.client.base_url is None
        assert seat.client.base_url_env == "WOPR_LLM_BASE_URL"
        assert seat.client.model is None
        assert seat.client.model_env == "WOPR_LLM_MODEL"
        assert seat.client.api_key_env == "TOGETHER_API_KEY"


def test_pilot_press_light_offline_variant_plays_one_validated_game() -> None:
    payload = json.loads(PRESS_LIGHT_PILOT.read_text(encoding="utf-8"))
    for seat in payload["seats"].values():
        seat["agent"] = "concordia_first_legal"
        del seat["client"]
    config = load_concordia_no_press_config(payload)

    result = run_concordia_no_press_game(config)

    validate_trace_artifact(result["trace_artifact"], result["replay"])
    assert result["summary"]["trace_count"] >= 1
    assert result["summary"]["press_message_count"] >= 1
    assert result["press_artifact"]["messages"]
