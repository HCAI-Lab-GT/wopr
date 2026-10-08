"""Expansion mechanic validation helpers."""

from __future__ import annotations

from typing import Any

from .action_models import ActionType
from .expansions import EXPANSION_MECHANICS, catalog_mode_gaps

EXPANSION_METADATA_STATUS = "rules_metadata_only"
POSTAL_BEHAVIOR_SOURCE = "UNOFF-001"


def validate_expansion_mechanics(
    registry: dict[str, Any],
) -> dict[str, list[dict[str, str]]]:
    registry_effects = _registry_effects(registry)
    expected_effects = {mechanic.postal_effect for mechanic in EXPANSION_MECHANICS}
    action_values = {action_type.value for action_type in ActionType}
    return {
        "missing_expansion_mechanics": [
            {
                "postal_effect": mechanic.postal_effect,
                "registry_id": mechanic.registry_id,
            }
            for mechanic in EXPANSION_MECHANICS
            if registry_effects.get(mechanic.postal_effect) != mechanic.registry_id
        ],
        "unexpected_expansion_mechanics": [
            {"postal_effect": effect, "registry_id": registry_id}
            for effect, registry_id in registry_effects.items()
            if effect not in expected_effects
        ],
        "expansion_action_gaps": [
            {"postal_effect": mechanic.postal_effect, "action_type": action_type}
            for mechanic in EXPANSION_MECHANICS
            for action_type in mechanic.action_types
            if action_type not in action_values
        ],
        "expansion_mode_gaps": catalog_mode_gaps(),
        "expansion_source_gaps": _source_boundary_gaps(registry),
    }


def _registry_effects(registry: dict[str, Any]) -> dict[str, str]:
    return {
        str(record.data["postal_effect"]): record.identifier
        for record in registry.values()
        if record.data.get("postal_effect")
    }


def _source_boundary_gaps(registry: dict[str, Any]) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    for mechanic in EXPANSION_MECHANICS:
        record = registry.get(mechanic.registry_id)
        if record is None:
            continue
        data = record.data
        if data.get("registry_status") != EXPANSION_METADATA_STATUS:
            gaps.append(
                _source_gap(
                    mechanic.postal_effect,
                    mechanic.registry_id,
                    "registry_status",
                    data.get("registry_status"),
                )
            )
        if data.get("count_in_deck") != 0:
            gaps.append(
                _source_gap(
                    mechanic.postal_effect,
                    mechanic.registry_id,
                    "count_in_deck",
                    data.get("count_in_deck"),
                )
            )
        sources = data.get("sources", [])
        if not isinstance(sources, list) or POSTAL_BEHAVIOR_SOURCE not in sources:
            gaps.append(
                _source_gap(
                    mechanic.postal_effect,
                    mechanic.registry_id,
                    "sources",
                    f"missing {POSTAL_BEHAVIOR_SOURCE}",
                )
            )
    return gaps


def _source_gap(
    postal_effect: str,
    registry_id: str,
    field: str,
    value: object,
) -> dict[str, str]:
    return {
        "postal_effect": postal_effect,
        "registry_id": registry_id,
        "field": field,
        "value": "<missing>" if value is None else str(value),
    }


__all__ = ["validate_expansion_mechanics"]
