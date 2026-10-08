"""Expansion mechanic catalog."""

from __future__ import annotations

from dataclasses import dataclass

from .action_models import ActionType

VALID_EXPANSION_MODES = {"postal", "table"}


@dataclass(frozen=True)
class ExpansionMechanic:
    postal_effect: str
    registry_id: str
    supported_modes: tuple[str, ...]
    action_types: tuple[str, ...] = ()


EXPANSION_MECHANICS = (
    ExpansionMechanic(
        "atomic_cannon",
        "nw_postal_atomic_cannon",
        ("postal",),
        (
            ActionType.POSTAL_ATOMIC_CANNON_SETUP.value,
            ActionType.POSTAL_ATOMIC_CANNON_FIRE.value,
            ActionType.POSTAL_ATOMIC_CANNON_REPOSITION.value,
        ),
    ),
    ExpansionMechanic(
        "cruise_missile",
        "nw_postal_cruise_missile",
        ("postal",),
        (
            ActionType.POSTAL_CRUISE_LAUNCH.value,
            ActionType.POSTAL_CRUISE_DROP.value,
            ActionType.POSTAL_CRUISE_MOVE.value,
        ),
    ),
    ExpansionMechanic(
        "killer_satellite",
        "nw_postal_killer_satellite",
        ("postal",),
        (
            ActionType.POSTAL_KILLER_SATELLITE_LAUNCH.value,
            ActionType.POSTAL_KILLER_SATELLITE_ATTACK.value,
        ),
    ),
    ExpansionMechanic("mx_missile", "nw_postal_mx_missile", ("postal",)),
    ExpansionMechanic(
        "sabotage",
        "nw_postal_saboteur",
        ("postal",),
        (ActionType.POSTAL_SABOTAGE.value,),
    ),
    ExpansionMechanic("smart_bomb", "nw_postal_smart_bomb", ("postal",)),
    ExpansionMechanic(
        "space_platform",
        "nw_postal_space_platform",
        ("postal",),
        (
            ActionType.POSTAL_SPACE_PLATFORM_LAUNCH.value,
            ActionType.POSTAL_SPACE_PLATFORM_DROP.value,
        ),
    ),
    ExpansionMechanic(
        "space_shuttle",
        "nw_postal_space_shuttle",
        ("postal",),
        (
            ActionType.POSTAL_SPACE_SHUTTLE_RELOAD.value,
            ActionType.POSTAL_SPACE_SHUTTLE_ATTACK.value,
        ),
    ),
    ExpansionMechanic(
        "submarine",
        "nw_postal_submarine",
        ("postal",),
        (
            ActionType.POSTAL_SUBMARINE_LAUNCH.value,
            ActionType.POSTAL_SUBMARINE_RELOAD.value,
            ActionType.POSTAL_SUBMARINE_FIRE.value,
            ActionType.POSTAL_SUBMARINE_RETURN.value,
        ),
    ),
    ExpansionMechanic(
        "supervirus",
        "nw_postal_supervirus",
        ("postal",),
        (
            ActionType.POSTAL_SUPERVIRUS_START.value,
            ActionType.POSTAL_SUPERVIRUS_PASS.value,
        ),
    ),
)


def catalog_effects() -> set[str]:
    return {mechanic.postal_effect for mechanic in EXPANSION_MECHANICS}


def catalog_registry_ids() -> set[str]:
    return {mechanic.registry_id for mechanic in EXPANSION_MECHANICS}


def catalog_mode_gaps() -> list[dict[str, str]]:
    gaps = [
        {"postal_effect": mechanic.postal_effect, "mode": mode}
        for mechanic in EXPANSION_MECHANICS
        for mode in mechanic.supported_modes
        if mode not in VALID_EXPANSION_MODES
    ]
    gaps.extend(
        {"postal_effect": mechanic.postal_effect, "mode": "<empty>"}
        for mechanic in EXPANSION_MECHANICS
        if not mechanic.supported_modes
    )
    return gaps


def catalog_payload() -> list[dict[str, object]]:
    return [
        {
            "postal_effect": mechanic.postal_effect,
            "registry_id": mechanic.registry_id,
            "supported_modes": list(mechanic.supported_modes),
            "action_types": list(mechanic.action_types),
        }
        for mechanic in EXPANSION_MECHANICS
    ]


__all__ = [
    "EXPANSION_MECHANICS",
    "ExpansionMechanic",
    "catalog_effects",
    "catalog_mode_gaps",
    "catalog_payload",
    "catalog_registry_ids",
]
