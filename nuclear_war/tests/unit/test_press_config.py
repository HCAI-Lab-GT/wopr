"""Press config parsing tests."""

from __future__ import annotations

import pytest

from nuclear_war_concordia.press_config import PressConfig, load_press_config


def test_load_press_config_defaults_to_none_when_absent() -> None:
    assert load_press_config(None) == PressConfig(mode="none", enabled=False)


def test_load_press_config_reads_press_light() -> None:
    config = load_press_config({"mode": "press_light", "enabled": True})

    assert config == PressConfig(mode="press_light", enabled=True)


@pytest.mark.parametrize(
    "payload",
    [
        {"mode": "press_light", "enabled": "true"},
        {"mode": "multi_turn_public", "enabled": True},
        {"mode": "press_light"},
        {"enabled": True},
        {"mode": "press_light", "enabled": True, "extra": 1},
    ],
)
def test_load_press_config_rejects_invalid(payload: dict) -> None:
    with pytest.raises(ValueError):
        load_press_config(payload)


def test_load_press_config_rejects_non_object() -> None:
    with pytest.raises(ValueError):
        load_press_config("press_light")


def test_load_press_config_reads_multi_turn_public() -> None:
    config = load_press_config(
        {"mode": "multi_turn_public", "enabled": True, "passes": 2}
    )

    assert config == PressConfig(mode="multi_turn_public", enabled=True, passes=2)


@pytest.mark.parametrize(
    "payload",
    [
        {"mode": "multi_turn_public", "enabled": True, "passes": 0},
        {"mode": "multi_turn_public", "enabled": True, "passes": -1},
        {"mode": "multi_turn_public", "enabled": True, "passes": 2.0},
        {"mode": "multi_turn_public", "enabled": True, "passes": "2"},
        {"mode": "multi_turn_public", "enabled": True},
        {"mode": "press_light", "enabled": True, "passes": 2},
        {"mode": "none", "enabled": False, "passes": 1},
    ],
)
def test_load_press_config_rejects_invalid_multi_turn(payload: dict) -> None:
    with pytest.raises(ValueError):
        load_press_config(payload)


def test_load_press_config_reads_full_press() -> None:
    config = load_press_config({"mode": "full_press", "enabled": True, "passes": 2})

    assert config == PressConfig(mode="full_press", enabled=True, passes=2)


@pytest.mark.parametrize(
    "payload",
    [
        {"mode": "full_press", "enabled": True, "passes": 0},
        {"mode": "full_press", "enabled": True, "passes": -1},
        {"mode": "full_press", "enabled": True, "passes": 2.0},
        {"mode": "full_press", "enabled": True, "passes": "2"},
        {"mode": "full_press", "enabled": True},
        {"mode": "full_press", "enabled": True, "passes": True},
    ],
)
def test_load_press_config_rejects_invalid_full_press(payload: dict) -> None:
    with pytest.raises(ValueError):
        load_press_config(payload)
