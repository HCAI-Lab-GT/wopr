"""Rendered observation validation for separate LLM trace artifacts."""

from __future__ import annotations

from typing import Any


def validate_trace_rendered_observation(trace: dict[str, Any], index: int) -> None:
    observation = trace["rendered_observation"]
    _validate_context_field(observation, trace, "player_id", index)
    _validate_context_field(observation, trace, "turn", index)
    _validate_decision_options(observation, trace, index)


def _validate_context_field(
    observation: dict[str, Any],
    trace: dict[str, Any],
    field: str,
    index: int,
) -> None:
    if observation.get(field) != trace[field]:
        raise ValueError(
            f"Trace {index} rendered_observation {field} does not match trace"
        )


def _validate_decision_options(
    observation: dict[str, Any],
    trace: dict[str, Any],
    index: int,
) -> None:
    decision = observation.get("decision")
    if isinstance(decision, dict) and "options" in decision:
        if decision["options"] != trace["legal_options"]:
            raise ValueError(
                f"Trace {index} rendered_observation decision options do not "
                "match legal_options"
            )


__all__ = ["validate_trace_rendered_observation"]
