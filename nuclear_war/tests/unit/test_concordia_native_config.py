"""Native Concordia harness config tests."""

from __future__ import annotations

from typing import cast

import pytest

from nuclear_war_concordia.config import load_concordia_no_press_config


def test_config_accepts_native_first_legal_agents() -> None:
    config = load_concordia_no_press_config(_payload("concordia_native_first_legal"))

    assert config.seats["player_0"].agent == "concordia_native_first_legal"


def test_config_accepts_native_http_agents_with_client() -> None:
    payload = _payload("concordia_native_http")
    seats = cast(dict[str, dict[str, object]], payload["seats"])
    for seat in seats.values():
        seat["client"] = {"base_url": "http://localhost:8000/v1", "model": "demo"}

    config = load_concordia_no_press_config(payload)

    assert config.seats["player_0"].client is not None


def test_native_http_requires_client() -> None:
    payload = _payload("concordia_native_http")

    with pytest.raises(ValueError, match="requires client"):
        load_concordia_no_press_config(payload)


def test_native_first_legal_rejects_client() -> None:
    payload = _payload("concordia_native_first_legal")
    seats = cast(dict[str, dict[str, object]], payload["seats"])
    seats["player_0"]["client"] = {
        "base_url": "http://localhost:8000/v1",
        "model": "demo",
    }

    with pytest.raises(ValueError, match="player_0 client"):
        load_concordia_no_press_config(payload)


def _payload(agent: str) -> dict[str, object]:
    return {
        "players": 4,
        "seed": 53,
        "max_turns": 1,
        "runtime": "auto",
        "seats": {
            f"player_{index}": {
                "agent": agent,
                "identity": {"name": f"Commander {index}"},
            }
            for index in range(4)
        },
    }
