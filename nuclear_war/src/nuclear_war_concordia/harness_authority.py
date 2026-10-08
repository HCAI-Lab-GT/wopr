"""Concordia command-authority seat construction."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nuclear_war_agents import DirectMemberFactory, FactionDecisionAgent

from .agent import ConcordiaDecisionAgent
from .authority_config import AuthorityConfig
from .harness_seat_runtime import ConcordiaSeatRuntime
from .types import ConcordiaClient


def build_authority_runtime(
    authority: AuthorityConfig,
    *,
    client_factory: Callable[[], ConcordiaClient],
    press_client_factory: Callable[[ConcordiaClient], ConcordiaClient] | None = None,
    max_retries: int,
) -> ConcordiaSeatRuntime:
    traces: dict[str, list[dict[str, Any]]] = {}
    members: list[tuple[str, ConcordiaDecisionAgent]] = []
    for config in authority.members:
        member_traces: list[dict[str, Any]] = []
        traces[config.member_id] = member_traces
        members.append(
            (
                config.member_id,
                ConcordiaDecisionAgent(
                    identity=dict(config.identity),
                    client=client_factory(),
                    trace_sink=member_traces,
                    max_retries=max_retries,
                ),
            )
        )
    member_agents = dict(members)
    spokesperson = member_agents[authority.spokesperson]
    return ConcordiaSeatRuntime(
        strategic_agent=FactionDecisionAgent(
            archetype=authority.archetype,
            subordinate_factory=DirectMemberFactory(members),
            archetype_parameters=dict(authority.parameters),
        ),
        spokesperson_client=(
            press_client_factory(spokesperson.client)
            if press_client_factory
            else spokesperson.client
        ),
        spokesperson_identity=dict(spokesperson.identity),
        memory_recipients=tuple(member_agents.values()),
        member_traces=traces,
    )


__all__ = ["build_authority_runtime"]
