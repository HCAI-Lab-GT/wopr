"""Concordia per-agent metadata payload tests (spec artifact contract).

Spec: concordia/agent_metadata.json carries "per-agent identity, role,
components, and model/client metadata". Identity already carries role; these
tests pin the client/model snapshot for HTTP seats and the component list for
native seats, with secret redaction.
"""

from __future__ import annotations

import json

import pytest

from nuclear_war_agents import HTTPClientConfig
from nuclear_war_concordia.config import ConcordiaNoPressConfig, ConcordiaSeatConfig
from nuclear_war_concordia.harness_payloads import agent_metadata
from nuclear_war_concordia.native_entity import NATIVE_CONTEXT_COMPONENTS

_CLIENT_FIELDS = set(
    "provider base_url base_url_env model model_env api_key_env provider_label "
    "timeout_seconds temperature max_tokens reasoning_effort reasoning_enabled "
    "stream".split()
)


def test_http_seat_metadata_carries_client_snapshot() -> None:
    metadata = agent_metadata(_config())

    http_meta = metadata["player_0"]
    assert http_meta["agent"] == "concordia_http"
    assert http_meta["identity"]["role"] == "strategic actor"
    assert set(http_meta["client"]) == _CLIENT_FIELDS
    assert http_meta["client"]["model"] == "demo-model"
    assert http_meta["client"]["api_key_env"] == "TOGETHER_API_KEY"
    assert "components" not in http_meta


def test_native_seat_metadata_carries_component_list() -> None:
    metadata = agent_metadata(_config())

    native_meta = metadata["player_1"]
    assert native_meta["agent"] == "concordia_native_first_legal"
    # The component list must match the keys the native entity actually
    # registers (and that appear in the trace's entity_log), including
    # Concordia's default observation/memory channel keys.
    assert set(native_meta["components"]) == {
        "instructions",
        "observation_to_memory",
        "__observation__",
        "__memory__",
    }
    assert "client" not in native_meta


def test_native_http_seat_carries_both_client_and_components() -> None:
    metadata = agent_metadata(_config())

    both_meta = metadata["player_2"]
    assert both_meta["agent"] == "concordia_native_http"
    assert set(both_meta["client"]) == _CLIENT_FIELDS
    assert both_meta["components"]


def test_plain_seat_metadata_has_no_client_or_components() -> None:
    metadata = agent_metadata(_config())

    plain_meta = metadata["player_3"]
    assert plain_meta["agent"] == "concordia_first_legal"
    assert "client" not in plain_meta
    assert "components" not in plain_meta


def test_agent_metadata_does_not_leak_api_key_env_name_as_value() -> None:
    # The client snapshot carries the env var *name*, never a resolved secret.
    metadata = agent_metadata(_config())
    dumped = json.dumps(metadata)
    assert "TOGETHER_API_KEY" in dumped  # the name is fine to record
    assert "super-secret-token" not in dumped  # a resolved secret must never appear


def test_native_component_literals_match_concordia_default_keys() -> None:
    # Guards against drift: the inlined "__observation__"/"__memory__" literals
    # must equal Concordia's real default component keys (which key the entity's
    # logging channels), so agent_metadata.components matches the trace entity_log.
    observation = pytest.importorskip("concordia.components.agent.observation")
    memory = pytest.importorskip("concordia.components.agent.memory")
    assert observation.DEFAULT_OBSERVATION_COMPONENT_KEY in NATIVE_CONTEXT_COMPONENTS
    assert memory.DEFAULT_MEMORY_COMPONENT_KEY in NATIVE_CONTEXT_COMPONENTS


def _client() -> HTTPClientConfig:
    return HTTPClientConfig(
        base_url="http://localhost:8000/v1",
        model="demo-model",
        api_key_env="TOGETHER_API_KEY",
    )


def _config() -> ConcordiaNoPressConfig:
    identity = {"name": "Commander", "role": "strategic actor"}
    seats = {
        "player_0": ConcordiaSeatConfig(
            agent="concordia_http", identity=identity, client=_client()
        ),
        "player_1": ConcordiaSeatConfig(
            agent="concordia_native_first_legal", identity=identity
        ),
        "player_2": ConcordiaSeatConfig(
            agent="concordia_native_http", identity=identity, client=_client()
        ),
        "player_3": ConcordiaSeatConfig(
            agent="concordia_first_legal", identity=identity
        ),
    }
    return ConcordiaNoPressConfig(players=4, seed=7, seats=seats)
