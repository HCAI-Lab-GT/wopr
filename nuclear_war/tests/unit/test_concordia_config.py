"""Concordia harness config tests."""

from __future__ import annotations

from typing import cast

import pytest

from nuclear_war_concordia.config import load_concordia_no_press_config


def test_load_concordia_no_press_config_accepts_four_style_agents() -> None:
    config = load_concordia_no_press_config(_payload())

    assert config.players == 4
    assert config.seed == 51
    assert config.max_turns == 10
    assert config.runtime == "auto"
    assert config.seats["player_0"].agent == "concordia_first_legal"
    assert config.seats["player_0"].identity["name"] == "Commander 0"


def test_load_concordia_no_press_config_rejects_non_four_player_count() -> None:
    payload = _payload()
    payload["players"] = 2
    seats = cast(dict[str, object], payload["seats"])
    del seats["player_2"]
    del seats["player_3"]

    with pytest.raises(ValueError, match="players must be exactly 4"):
        load_concordia_no_press_config(payload)


def test_load_concordia_no_press_config_rejects_missing_seat() -> None:
    payload = _payload()
    seats = cast(dict[str, object], payload["seats"])
    del seats["player_3"]

    with pytest.raises(ValueError, match="must match players"):
        load_concordia_no_press_config(payload)


def test_load_concordia_no_press_config_rejects_unknown_field() -> None:
    payload = _payload()
    payload["extra"] = True

    with pytest.raises(ValueError, match="fields are invalid"):
        load_concordia_no_press_config(payload)


def test_load_concordia_config_rejects_first_legal_scripted_responses() -> None:
    payload = _payload()
    seats = cast(dict[str, dict[str, object]], payload["seats"])
    seats["player_0"]["scripted_responses"] = ["ignored"]

    with pytest.raises(ValueError, match="player_0 scripted_responses"):
        load_concordia_no_press_config(payload)


def test_load_concordia_no_press_config_rejects_scripted_client() -> None:
    payload = _payload()
    seats = cast(dict[str, dict[str, object]], payload["seats"])
    seats["player_0"]["agent"] = "concordia_scripted"
    seats["player_0"]["scripted_responses"] = ['{"action_id": "player_0:draw"}']
    seats["player_0"]["client"] = _client_payload()

    with pytest.raises(ValueError, match="player_0 client"):
        load_concordia_no_press_config(payload)


def test_load_concordia_no_press_config_rejects_http_scripted_responses() -> None:
    payload = _payload()
    seats = cast(dict[str, dict[str, object]], payload["seats"])
    seats["player_0"]["agent"] = "concordia_http"
    seats["player_0"]["client"] = _client_payload()
    seats["player_0"]["scripted_responses"] = ["ignored"]

    with pytest.raises(ValueError, match="player_0 scripted_responses"):
        load_concordia_no_press_config(payload)


def _client_payload() -> dict[str, object]:
    return {
        "base_url": "http://localhost:8000/v1",
        "model": "demo-model",
    }


def _payload() -> dict[str, object]:
    return {
        "players": 4,
        "seed": 51,
        "max_turns": 10,
        "runtime": "auto",
        "seats": {
            f"player_{index}": {
                "agent": "concordia_first_legal",
                "identity": {
                    "name": f"Commander {index}",
                    "role": "strategic actor",
                    "objective": "survive the game",
                },
                "max_retries": 1,
            }
            for index in range(4)
        },
    }
