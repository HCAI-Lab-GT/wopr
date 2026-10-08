"""Schema validation for C2 deliberation sidecars."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.replay_validation import validate_replay_payload

from .c2_aggregation_validation import validate_c2_aggregation
from .c2_identity_validation import validate_c2_deliberation_identity
from .c2_replay_validation import validate_c2_replay_alignment
from .c2_trace_validation import (
    validate_c2_member_consistency,
    validate_c2_member_trace,
)

C2_SCHEMA_VERSION = 1
_ARTIFACT_FIELDS = {
    "schema_version",
    "replay",
    "authority_players",
    "deliberations",
}
_DELIBERATION_FIELDS = {
    "deliberation_id",
    "player_id",
    "turn",
    "decision_type",
    "archetype",
    "parameters",
    "rule",
    "selected_action_id",
    "members",
}
_MEMBER_FIELDS = {"member_id", "vote_action_id", "trace_ref", "trace"}


def validate_c2_artifact(payload: Any, replay: dict[str, Any]) -> None:
    validate_replay_payload(replay)
    if not isinstance(payload, dict):
        raise ValueError("C2 artifact must be an object")
    if set(payload) != _ARTIFACT_FIELDS:
        raise ValueError("C2 artifact fields are invalid")
    schema_version = payload["schema_version"]
    if type(schema_version) is not int or schema_version != C2_SCHEMA_VERSION:
        raise ValueError("C2 artifact schema_version is invalid")
    if payload["replay"] != c2_replay_reference(replay):
        raise ValueError("C2 artifact replay reference does not match replay")
    deliberations = payload["deliberations"]
    if not isinstance(deliberations, list):
        raise ValueError("C2 artifact deliberations must be a list")
    seen_deliberation_ids: set[str] = set()
    next_deliberation_indices: dict[str, int] = {}
    seen_refs: set[str] = set()
    for index, deliberation in enumerate(deliberations):
        _validate_deliberation_shape(
            deliberation,
            index,
            seen_deliberation_ids,
            next_deliberation_indices,
            seen_refs,
        )
    validate_c2_replay_alignment(
        deliberations,
        payload["authority_players"],
        replay,
    )
    for index, deliberation in enumerate(deliberations):
        validate_c2_aggregation(deliberation, index)


def _validate_deliberation_shape(
    deliberation: Any,
    index: int,
    seen_deliberation_ids: set[str],
    next_deliberation_indices: dict[str, int],
    seen_refs: set[str],
) -> None:
    if not isinstance(deliberation, dict):
        raise ValueError(f"C2 deliberation {index} must be an object")
    if set(deliberation) != _DELIBERATION_FIELDS:
        raise ValueError(f"C2 deliberation {index} fields are invalid")
    validate_c2_deliberation_identity(
        deliberation,
        seen_deliberation_ids,
        next_deliberation_indices,
    )
    members = deliberation["members"]
    if not isinstance(members, list) or len(members) != 3:
        raise ValueError(f"C2 deliberation {index} requires exactly three members")
    member_ids: set[str] = set()
    for member_index, member in enumerate(members):
        _validate_member_shape(
            member,
            deliberation,
            index,
            member_index,
            member_ids,
            seen_refs,
        )
    validate_c2_member_consistency(deliberation, index)


def _validate_member_shape(
    member: Any,
    deliberation: dict[str, Any],
    index: int,
    member_index: int,
    member_ids: set[str],
    seen_refs: set[str],
) -> None:
    if not isinstance(member, dict) or set(member) != _MEMBER_FIELDS:
        raise ValueError(
            f"C2 deliberation {index} member {member_index} fields invalid"
        )
    member_id = member["member_id"]
    if not isinstance(member_id, str) or not member_id or member_id in member_ids:
        raise ValueError(f"C2 deliberation {index} member ids must be unique")
    member_ids.add(member_id)
    trace_ref = member["trace_ref"]
    if not isinstance(trace_ref, str) or not trace_ref or trace_ref in seen_refs:
        raise ValueError(f"C2 deliberation {index} duplicate trace_ref")
    seen_refs.add(trace_ref)
    if trace_ref != f"{deliberation['deliberation_id']}:{member_id}":
        raise ValueError(f"C2 deliberation {index} trace_ref scope is invalid")
    validate_c2_member_trace(member, deliberation, index * 3 + member_index)


def c2_replay_reference(replay: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": replay["mode"],
        "seed": replay["seed"],
        "agent": replay["agent"],
        "players": replay["players"],
        "turns": replay["turns"],
    }


__all__ = ["C2_SCHEMA_VERSION", "c2_replay_reference", "validate_c2_artifact"]
