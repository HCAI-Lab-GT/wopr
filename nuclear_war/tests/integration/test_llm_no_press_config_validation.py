"""No-press LLM config validation tests."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import pytest

from nuclear_war_env.cli import main
from nuclear_war_env.llm_harness_batch import load_no_press_llm_batch_config


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (
            lambda payload: payload["seats"].__setitem__(0, {"agent": "random"}),
            "seat ids",
        ),
        (
            lambda payload: _seat(payload).__setitem__("agent", 7),
            "agent must be a string",
        ),
        (
            lambda payload: _seat(payload).__setitem__("agent", "unknown"),
            "agent must be one of",
        ),
        (
            lambda payload: _seat(payload).__setitem__("scripted_responses", "bad"),
            "scripted_responses must be a list",
        ),
        (
            lambda payload: _seat(payload).__setitem__("scripted_responses", [7]),
            "scripted_responses entries must be strings",
        ),
        (
            lambda payload: _seat(payload).__setitem__(
                "scripted_provider_latency_ms", [True]
            ),
            "scripted_provider_latency_ms entries must be integers",
        ),
        (
            lambda payload: _seat(payload).__setitem__("scripted_provider_cost", ["1"]),
            "scripted_provider_cost entries must be numbers",
        ),
        (
            lambda payload: _seat(payload).__setitem__("max_retries", True),
            "max_retries must be an integer",
        ),
        (
            lambda payload: _seat(payload).__setitem__("max_retries", -1),
            "max_retries must be non-negative",
        ),
        (
            lambda payload: _seat(payload).__setitem__("fallback", "last"),
            "fallback must be one of",
        ),
    ],
)
def test_llm_batch_config_rejects_invalid_seat_fields(
    mutator: Callable[[dict[str, Any]], object],
    message: str,
) -> None:
    payload = _config_payload()
    mutator(payload)

    with pytest.raises(ValueError, match=message):
        load_no_press_llm_batch_config(payload)


def test_cli_llm_experiment_rejects_invalid_config(tmp_path, capsys) -> None:
    config_path = tmp_path / "llm_config.json"
    payload = _config_payload()
    _seat(payload)["max_retries"] = True
    config_path.write_text(json.dumps(payload), encoding="utf-8")

    code = main(
        ["llm-experiment", "--config", str(config_path), "--out-dir", str(tmp_path)]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "LLM experiment seat player_0 max_retries must be an integer" in captured.err


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (
            lambda payload: payload["seats"].pop("player_3"),
            "seats must match players",
        ),
        (
            lambda payload: payload["seats"].__setitem__(
                "player_4",
                {"agent": "random"},
            ),
            "seats must match players",
        ),
        (lambda payload: payload.__setitem__("runs", 0), "runs must be positive"),
        (
            lambda payload: payload.__setitem__("max_turns", 0),
            "max_turns must be positive",
        ),
        (
            lambda payload: payload.__setitem__("players", 1),
            "players must be at least 2",
        ),
    ],
)
def test_llm_batch_config_rejects_invalid_experiment_bounds(
    mutator: Callable[[dict[str, Any]], object],
    message: str,
) -> None:
    payload = _config_payload()
    mutator(payload)

    with pytest.raises(ValueError, match=message):
        load_no_press_llm_batch_config(payload)


@pytest.mark.parametrize(
    "archetype_parameters",
    [
        None,
        {},
        {"policy_action_id": 7},
        {"policy_action_id": ""},
    ],
)
def test_llm_batch_config_rejects_automated_faction_without_policy_action_id(
    archetype_parameters: Any,
) -> None:
    payload = _automated_faction_payload(archetype_parameters)

    with pytest.raises(ValueError, match="policy_action_id"):
        load_no_press_llm_batch_config(payload)


def test_llm_batch_config_accepts_automated_faction_with_policy_action_id() -> None:
    payload = _automated_faction_payload({"policy_action_id": "player_0:pass"})

    config = load_no_press_llm_batch_config(payload)

    assert config.seats["player_0"].archetype == "automated"
    assert config.seats["player_0"].archetype_parameters == {
        "policy_action_id": "player_0:pass"
    }


def _automated_faction_payload(archetype_parameters: Any) -> dict[str, Any]:
    seat: dict[str, Any] = {
        "agent": "faction_c2",
        "archetype": "automated",
        "members": [{"member_id": "advisor_a", "agent": "llm_first_legal"}],
    }
    if archetype_parameters is not None:
        seat["archetype_parameters"] = archetype_parameters
    return {
        "players": 2,
        "seed_start": 7,
        "runs": 1,
        "max_turns": 3,
        "seats": {"player_0": seat, "player_1": {"agent": "heuristic"}},
    }


def _seat(payload: dict[str, Any]) -> dict[str, Any]:
    return payload["seats"]["player_0"]


def _config_payload() -> dict[str, Any]:
    return {
        "players": 4,
        "seed_start": 31,
        "runs": 1,
        "max_turns": 1,
        "seats": {
            "player_0": {
                "agent": "llm_scripted",
                "scripted_responses": ['{"action_id": "player_0:draw"}'],
            },
            "player_1": {"agent": "random"},
            "player_2": {"agent": "heuristic"},
            "player_3": {"agent": "decision_heuristic"},
        },
    }
