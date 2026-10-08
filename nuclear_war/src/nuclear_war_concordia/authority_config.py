"""Command-authority config parsing for Concordia seats."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from nuclear_war_env import llm_harness_batch_config_values as values

from .authority_parameters import normalized_authority_parameters
from .config_values import load_identity, nonempty_str_value, validate_fields

AUTHORITY_FIELDS = {"archetype", "parameters", "spokesperson", "members"}
MEMBER_FIELDS = {"member_id", "identity"}
AUTHORITY_ARCHETYPES = {"council", "sole_authority"}


@dataclass(frozen=True)
class AuthorityMemberConfig:
    member_id: str
    identity: Mapping[str, str]


@dataclass(frozen=True)
class AuthorityConfig:
    archetype: str
    parameters: Mapping[str, Any]
    spokesperson: str
    members: tuple[AuthorityMemberConfig, ...]


def load_authority_config(payload: Any, context: str) -> AuthorityConfig | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise ValueError(f"{context} authority must be an object")
    validate_fields(payload, AUTHORITY_FIELDS, f"{context} authority")
    members = payload.get("members")
    if not isinstance(members, list):
        raise ValueError(f"{context} authority members must be a list")
    if len(members) != 3:
        raise ValueError(f"{context} authority requires exactly three members")
    if "parameters" not in payload:
        raise ValueError(f"{context} authority requires parameters")
    parameters = payload["parameters"]
    if not isinstance(parameters, dict):
        raise ValueError(f"{context} authority parameters must be an object")
    parsed_members = tuple(_member_config(member, context) for member in members)
    return _validated_authority(payload, parameters, parsed_members, context)


def _validated_authority(
    payload: dict[str, Any],
    parameters: dict[Any, Any],
    parsed_members: tuple[AuthorityMemberConfig, ...],
    context: str,
) -> AuthorityConfig:
    member_ids = [member.member_id for member in parsed_members]
    if len(set(member_ids)) != len(member_ids):
        raise ValueError(f"{context} authority member ids must be unique")
    member_names = [member.identity["name"] for member in parsed_members]
    if len(set(member_names)) != len(member_names):
        raise ValueError(f"{context} authority member names must be unique")
    spokesperson = values.str_value(payload, "spokesperson", context=context)
    if spokesperson not in member_ids:
        raise ValueError(f"{context} authority spokesperson must name a member")
    archetype = values.str_value(payload, "archetype", context=context)
    if archetype not in AUTHORITY_ARCHETYPES:
        allowed = sorted(AUTHORITY_ARCHETYPES)
        raise ValueError(f"{context} authority archetype must be one of {allowed}")
    if archetype == "sole_authority" and "executive" not in member_ids:
        raise ValueError(f"{context} sole authority requires an executive member")
    return AuthorityConfig(
        archetype=archetype,
        parameters=normalized_authority_parameters(
            archetype, parameters, member_ids, context
        ),
        spokesperson=spokesperson,
        members=parsed_members,
    )


def _member_config(payload: Any, context: str) -> AuthorityMemberConfig:
    if not isinstance(payload, dict):
        raise ValueError(f"{context} authority members must be objects")
    member_context = f"{context} authority member"
    validate_fields(payload, MEMBER_FIELDS, member_context)
    return AuthorityMemberConfig(
        member_id=nonempty_str_value(payload, "member_id", member_context),
        identity=load_identity(
            payload.get("identity"),
            member_context,
            require_nonempty_name=True,
        ),
    )


__all__ = ["AuthorityConfig", "AuthorityMemberConfig", "load_authority_config"]
