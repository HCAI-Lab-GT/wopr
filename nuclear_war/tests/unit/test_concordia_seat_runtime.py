"""Concordia seat-runtime behavior tests."""

from __future__ import annotations

from typing import cast

from nuclear_war_agents import FactionDecisionAgent
from nuclear_war_concordia.agent import ConcordiaDecisionAgent
from nuclear_war_concordia.config import load_concordia_no_press_config
from nuclear_war_concordia.harness_agents import build_seat_runtimes


def test_single_seat_runtime_preserves_agent_and_press_surfaces(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    del _seat(payload)["authority"]
    config = load_concordia_no_press_config(payload)

    runtime = build_seat_runtimes(config, [], "fallback")["player_0"]

    agent = runtime.strategic_agent
    assert isinstance(agent, ConcordiaDecisionAgent)
    assert runtime.memory_recipients == (agent,)
    assert runtime.spokesperson_client is agent.client
    assert runtime.spokesperson_identity == dict(agent.identity)

    messages = [{"speaker": "player_1", "text": "hold", "visibility": "public"}]
    runtime.set_press_memory(messages)

    assert agent.press_memory == messages


def test_authority_runtime_fans_memory_to_members_and_exposes_spokesperson(
    authority_config_payload: dict[str, object],
) -> None:
    authority = cast(dict[str, object], _seat(authority_config_payload)["authority"])
    authority["spokesperson"] = "risk_advisor"
    config = load_concordia_no_press_config(authority_config_payload)

    runtime = build_seat_runtimes(config, [], "fallback")["player_0"]

    assert isinstance(runtime.strategic_agent, FactionDecisionAgent)
    assert [agent.identity["name"] for agent in runtime.memory_recipients] == [
        "Executive",
        "Strategic Advisor",
        "Risk Advisor",
    ]
    risk_advisor = runtime.memory_recipients[2]
    assert runtime.spokesperson_client is risk_advisor.client
    assert runtime.spokesperson_identity == dict(risk_advisor.identity)
    assert set(runtime.member_traces) == {
        "executive",
        "strategic_advisor",
        "risk_advisor",
    }
    member_ids = ("executive", "strategic_advisor", "risk_advisor")
    for member_id, agent in zip(member_ids, runtime.memory_recipients, strict=True):
        assert agent.trace_sink is runtime.member_traces[member_id]
    assert len({id(sink) for sink in runtime.member_traces.values()}) == 3

    messages = [{"speaker": "player_1", "text": "hold", "visibility": "public"}]
    runtime.set_press_memory(messages)

    assert all(agent.press_memory == messages for agent in runtime.memory_recipients)
    assert len({id(agent.press_memory) for agent in runtime.memory_recipients}) == 3


def _seat(payload: dict[str, object]) -> dict[str, object]:
    seats = cast(dict[str, dict[str, object]], payload["seats"])
    return seats["player_0"]
