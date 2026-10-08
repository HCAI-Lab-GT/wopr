"""Normalized experimental-condition payloads."""

from __future__ import annotations

from typing import Any

from .authority_config import AuthorityConfig
from .press_config import PressConfig


def authority_snapshot(authority: AuthorityConfig) -> dict[str, Any]:
    return {
        "archetype": authority.archetype,
        "parameters": dict(authority.parameters),
        "spokesperson": authority.spokesperson,
        "members": [
            {
                "member_id": member.member_id,
                "identity": dict(member.identity),
            }
            for member in authority.members
        ],
    }


def press_snapshot(press: PressConfig) -> dict[str, object]:
    return {
        "mode": press.mode,
        "enabled": press.enabled,
        "passes": press.passes,
    }


__all__ = ["authority_snapshot", "press_snapshot"]
