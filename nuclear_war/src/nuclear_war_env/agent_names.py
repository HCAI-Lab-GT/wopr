"""Public simulation and replay agent names."""

from __future__ import annotations

DECISION_HEURISTIC_AGENT = "decision_heuristic"
# Honest replay label for the injected-decision-agent harnesses (Concordia
# no-press and the native LLM harness): when seat agents are injected via
# run_table_simulation_with_decision_agents there is no single driver policy, so
# the replay "agent" field is "mixed_seats" instead of borrowing one seat's label.
# The authoritative per-seat agents live in each harness's agent_metadata and
# trace sidecars. This is a replay/metadata label only: no single-agent run path
# builds it, so it is not a `simulate --agent` choice.
MIXED_SEATS_AGENT = "mixed_seats"

SIMULATION_AGENT_NAMES = (
    "random",
    "heuristic",
    "interactive",
    DECISION_HEURISTIC_AGENT,
)
# Agent labels that may legitimately appear in a replay/config. Superset of the
# runnable single-agent names, plus the per-seat label emitted by the decision-
# agent harnesses.
REPLAY_AGENT_NAMES = (*SIMULATION_AGENT_NAMES, MIXED_SEATS_AGENT)
EXPERIMENT_AGENT_NAMES = ("random", "heuristic", DECISION_HEURISTIC_AGENT)


def reject_table_only_agent(agent: str, mode: str, context: str) -> None:
    if agent == DECISION_HEURISTIC_AGENT and mode != "table":
        raise ValueError(f"{context} agent {DECISION_HEURISTIC_AGENT} is table-only")


__all__ = [
    "DECISION_HEURISTIC_AGENT",
    "EXPERIMENT_AGENT_NAMES",
    "MIXED_SEATS_AGENT",
    "REPLAY_AGENT_NAMES",
    "SIMULATION_AGENT_NAMES",
    "reject_table_only_agent",
]
