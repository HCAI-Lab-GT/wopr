"""Source provenance validation for rule data."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_RESEARCH_IMPORTS = Path(__file__).resolve().parents[2] / "research" / "imports"
_SOURCE_BUNDLE = "2026-06-14_nuclear_war_card_game_research_bundle"
SOURCE_INDEX_PATH = _RESEARCH_IMPORTS / _SOURCE_BUNDLE / "source_index.json"
SOURCE_ID_PATTERN = re.compile(r"^[A-Z]+-\d{3}$")
VALID_CONFIDENCE_VALUES = {"high", "low", "medium"}


def source_id_is_valid(source_id: object) -> bool:
    return (
        isinstance(source_id, str)
        and bool(source_id)
        and source_id.strip() == source_id
        and bool(SOURCE_ID_PATTERN.fullmatch(source_id))
    )


def unresolved_source_labels(
    registry: dict[str, Any],
    source_ids: set[str],
) -> list[dict[str, str]]:
    unresolved: list[dict[str, str]] = []
    for record in registry.values():
        sources = record.data.get("sources", [])
        if not isinstance(sources, list):
            unresolved.append({"card_id": record.identifier, "source": str(sources)})
            continue
        for source in sources:
            source_id = str(source)
            if source_id not in source_ids:
                unresolved.append({"card_id": record.identifier, "source": source_id})
    return unresolved


def missing_source_fields(registry: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for record in registry.values():
        sources = record.data.get("sources")
        if not isinstance(sources, list) or not sources:
            missing.append(record.identifier)
    return sorted(missing)


def invalid_source_fields(registry: dict[str, Any]) -> list[dict[str, object]]:
    invalid: list[dict[str, object]] = []
    for record in registry.values():
        sources = record.data.get("sources")
        if not isinstance(sources, list):
            invalid.append({"card_id": record.identifier, "source": sources})
            continue
        for source in sources:
            if not source_id_is_valid(source):
                invalid.append({"card_id": record.identifier, "source": source})
    return invalid


def missing_confidence_fields(registry: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for record in registry.values():
        confidence = record.data.get("confidence")
        if not isinstance(confidence, str) or not confidence.strip():
            missing.append(record.identifier)
    return sorted(missing)


def invalid_confidence_fields(registry: dict[str, Any]) -> list[dict[str, str]]:
    invalid: list[dict[str, str]] = []
    for record in registry.values():
        confidence = record.data.get("confidence")
        if not isinstance(confidence, str) or not confidence.strip():
            continue
        normalized = confidence.strip().lower()
        if normalized not in VALID_CONFIDENCE_VALUES:
            invalid.append(
                {"card_id": record.identifier, "confidence": str(confidence)}
            )
    return invalid


def invalid_count_fields(registry: dict[str, Any]) -> list[dict[str, object]]:
    invalid: list[dict[str, object]] = []
    for record in registry.values():
        count = record.data.get("count_in_deck", 1)
        if not isinstance(count, int) or isinstance(count, bool) or count < 0:
            invalid.append({"card_id": record.identifier, "count_in_deck": count})
    return invalid


def metadata_records_in_deck(registry: dict[str, Any]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for record in registry.values():
        if record.data.get("registry_status") != "rules_metadata_only":
            continue
        count = record.data.get("count_in_deck", 0)
        if count is True:
            records.append({"card_id": record.identifier, "count_in_deck": count})
        if isinstance(count, int) and not isinstance(count, bool) and count > 0:
            records.append({"card_id": record.identifier, "count_in_deck": count})
    return records


def restricted_text_fields(
    registry: dict[str, Any],
    restricted_names: set[str],
) -> list[dict[str, str]]:
    matches: list[dict[str, str]] = []
    for record in registry.values():
        for field in _restricted_paths(record.data, restricted_names):
            matches.append({"card_id": record.identifier, "field": field})
    return matches


def _restricted_paths(
    value: Any,
    restricted_names: set[str],
    prefix: str = "",
) -> list[str]:
    if isinstance(value, dict):
        matches: list[str] = []
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in restricted_names:
                matches.append(path)
            matches.extend(_restricted_paths(item, restricted_names, path))
        return matches
    if isinstance(value, list):
        matches = []
        for index, item in enumerate(value):
            path = f"{prefix}.{index}" if prefix else str(index)
            matches.extend(_restricted_paths(item, restricted_names, path))
        return matches
    return []
