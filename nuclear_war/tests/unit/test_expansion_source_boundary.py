"""Expansion source-boundary validation tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.rules import RULES_PATH, validate_rules


def test_validate_rules_reports_no_expansion_source_gaps() -> None:
    payload = validate_rules()

    assert payload["expansion_source_gaps"] == []


def test_validate_rules_rejects_playable_expansion_metadata(
    tmp_path: Path,
) -> None:
    records = _registry_records()
    cruise = next(
        record for record in records if record["id"] == "nw_postal_cruise_missile"
    )
    cruise["registry_status"] = "playable"
    cruise["count_in_deck"] = 1
    registry_path = _write_registry(tmp_path, records)

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["expansion_source_gaps"] == [
        {
            "postal_effect": "cruise_missile",
            "registry_id": "nw_postal_cruise_missile",
            "field": "registry_status",
            "value": "playable",
        },
        {
            "postal_effect": "cruise_missile",
            "registry_id": "nw_postal_cruise_missile",
            "field": "count_in_deck",
            "value": "1",
        },
    ]


def test_validate_rules_requires_postal_source_for_expansion_metadata(
    tmp_path: Path,
) -> None:
    records = _registry_records()
    cruise = next(
        record for record in records if record["id"] == "nw_postal_cruise_missile"
    )
    cruise["sources"] = ["COMM-002"]
    registry_path = _write_registry(tmp_path, records)

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["expansion_source_gaps"] == [
        {
            "postal_effect": "cruise_missile",
            "registry_id": "nw_postal_cruise_missile",
            "field": "sources",
            "value": "missing UNOFF-001",
        }
    ]


def _registry_records() -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in RULES_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _write_registry(tmp_path: Path, records: list[dict[str, object]]) -> Path:
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )
    return registry_path
