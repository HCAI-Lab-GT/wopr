"""Concordia example config tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_concordia.config import load_concordia_no_press_config


def test_concordia_style_demo_config_loads() -> None:
    config = load_concordia_no_press_config(
        json.loads(_example("concordia_no_press_style_demo.json").read_text())
    )

    assert config.players == 4
    assert all(seat.agent == "concordia_first_legal" for seat in config.seats.values())


def test_concordia_together_demo_config_loads() -> None:
    config = load_concordia_no_press_config(
        json.loads(_example("concordia_no_press_together_demo.json").read_text())
    )

    assert config.players == 4
    assert all(seat.agent == "concordia_native_http" for seat in config.seats.values())
    assert config.seats["player_0"].client is not None
    assert config.seats["player_0"].client.provider == "together"
    assert config.seats["player_0"].client.model == "openai/gpt-oss-20b"
    assert config.seats["player_0"].client.model_env == "TOGETHER_MODEL"


def test_concordia_native_demo_config_loads() -> None:
    config = load_concordia_no_press_config(
        json.loads(_example("concordia_no_press_native_demo.json").read_text())
    )

    assert config.players == 4
    assert all(
        seat.agent == "concordia_native_first_legal" for seat in config.seats.values()
    )


def _example(name: str) -> Path:
    return Path("docs/examples") / name
