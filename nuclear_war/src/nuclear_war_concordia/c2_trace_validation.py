"""Member-trace validation for C2 deliberation sidecars."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.llm_trace_artifact_schema import validate_trace_schema
from nuclear_war_env.llm_trace_identity import validate_trace_identity
from nuclear_war_env.llm_trace_legal_options import validate_trace_legal_options
from nuclear_war_env.llm_trace_rendered_observation import (
    validate_trace_rendered_observation,
)

C2_TRACE_SCHEMA_VERSION = 5
_DECISION_TYPES = {item.value for item in DecisionType}


def validate_c2_member_trace(
    member: dict[str, Any],
    deliberation: dict[str, Any],
    trace_index: int,
) -> None:
    trace = member["trace"]
    if not isinstance(trace, dict):
        raise ValueError(f"C2 member trace {trace_index} must be an object")
    validate_trace_schema(trace, trace_index, C2_TRACE_SCHEMA_VERSION)
    validate_trace_identity(trace, trace_index)
    validate_trace_rendered_observation(trace, trace_index)
    _validate_decision_type(trace, trace_index)
    if trace["fallback_used"]:
        raise ValueError(f"C2 member trace {trace_index} must not use fallback")
    if trace["validation_errors"]:
        raise ValueError(f"C2 member trace {trace_index} has a malformed attempt")
    validate_trace_legal_options(trace, trace_index)
    _validate_context(trace, deliberation, trace_index)
    legal_ids = {option["action_id"] for option in trace["legal_options"]}
    vote_action_id = member["vote_action_id"]
    if not isinstance(vote_action_id, str) or not vote_action_id:
        raise ValueError(
            f"C2 member trace {trace_index} vote_action_id must be a string"
        )
    if vote_action_id not in legal_ids:
        raise ValueError(f"C2 member trace {trace_index} vote action is not legal")
    if vote_action_id != trace["selected_action_id"]:
        raise ValueError(f"C2 member trace {trace_index} vote does not match trace")


def validate_c2_member_consistency(deliberation: dict[str, Any], index: int) -> None:
    members = deliberation["members"]
    expected_options = members[0]["trace"]["legal_options"]
    sequence = deliberation["deliberation_id"].rsplit(":", 1)[1]
    expected_trace_id = f"{deliberation['player_id']}:{deliberation['turn']}:{sequence}"
    for member in members:
        trace = member["trace"]
        if trace["legal_options"] != expected_options:
            raise ValueError(
                f"C2 deliberation {index} member legal options do not match"
            )
        if trace["trace_id"] != expected_trace_id:
            raise ValueError(
                f"C2 deliberation {index} trace_id does not match deliberation"
            )


def _validate_context(
    trace: dict[str, Any],
    deliberation: dict[str, Any],
    trace_index: int,
) -> None:
    for field in ("player_id", "turn", "decision_type"):
        if trace[field] != deliberation[field]:
            raise ValueError(
                f"C2 member trace {trace_index} {field} does not match deliberation"
            )


def _validate_decision_type(trace: dict[str, Any], trace_index: int) -> None:
    decision_type = trace["decision_type"]
    decision = trace["rendered_observation"].get("decision")
    if decision_type not in _DECISION_TYPES:
        raise ValueError(f"C2 member trace {trace_index} decision_type is invalid")
    if not isinstance(decision, dict) or decision.get("decision_type") != decision_type:
        raise ValueError(
            f"C2 member trace {trace_index} decision_type does not match observation"
        )


__all__ = [
    "C2_TRACE_SCHEMA_VERSION",
    "validate_c2_member_consistency",
    "validate_c2_member_trace",
]
