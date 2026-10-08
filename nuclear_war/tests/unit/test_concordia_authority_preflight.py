"""Offline resolution tests for HTTP authority configurations."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any, cast

import pytest

from nuclear_war_env.llm_preflight import resolve_llm_preflight_config


def test_authority_preflight_resolves_client_and_metadata_without_network(
    authority_config_payload: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WOPR_TEST_API_KEY", "secret-value")

    def fail_if_called(*args: object, **kwargs: object) -> None:
        pytest.fail("offline authority preflight contacted a provider")

    monkeypatch.setattr(
        "nuclear_war_env.llm_preflight.LLMHttpClient.complete", fail_if_called
    )
    payload = deepcopy(authority_config_payload)
    payload["press"] = {"mode": "full_press", "enabled": True, "passes": 1}
    seats = cast(dict[str, dict[str, Any]], payload["seats"])
    seat = seats["player_0"]
    seat["agent"] = "concordia_http"
    seat["client"] = {
        "base_url_env": "WOPR_LLM_BASE_URL",
        "model_env": "WOPR_LLM_MODEL",
        "api_key_env": "WOPR_TEST_API_KEY",
        "provider_label": "direct_api",
    }
    authority = cast(dict[str, Any], seat["authority"])
    authority["archetype"] = "council"
    authority["parameters"] = {
        "threshold": 0.5,
        "weights": {
            "executive": 1.0,
            "strategic_advisor": 1.0,
            "risk_advisor": 1.0,
        },
    }
    report = resolve_llm_preflight_config(payload)

    assert report["config_kind"] == "concordia"
    assert report["seat"] == "player_0"
    assert report["client"]["base_url_env"] == "WOPR_LLM_BASE_URL"
    assert report["client"]["model_env"] == "WOPR_LLM_MODEL"
    assert report["client"]["api_key_env"] == "WOPR_TEST_API_KEY"
    assert report["press"] == {
        "mode": "full_press",
        "enabled": True,
        "passes": 1,
    }
    assert report["authority"] == authority
    assert "secret-value" not in json.dumps(report)
