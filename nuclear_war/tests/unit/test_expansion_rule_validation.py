"""Expansion rule validation tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.rules import RULES_PATH, validate_rules


def test_validate_rules_reports_expansion_mechanic_catalog() -> None:
    payload = validate_rules()

    assert {item["postal_effect"] for item in payload["expansion_mechanics"]} == {
        "atomic_cannon",
        "cruise_missile",
        "killer_satellite",
        "mx_missile",
        "sabotage",
        "smart_bomb",
        "space_platform",
        "space_shuttle",
        "submarine",
        "supervirus",
    }
    assert payload["missing_expansion_mechanics"] == []
    assert payload["unexpected_expansion_mechanics"] == []
    assert payload["expansion_action_gaps"] == []


def test_validate_rules_reports_no_expansion_mode_gaps() -> None:
    payload = validate_rules()

    assert payload["expansion_mode_gaps"] == []


def test_validate_rules_reports_missing_expansion_registry_record(
    tmp_path: Path,
) -> None:
    records = [
        record
        for record in _registry_records()
        if record["id"] != "nw_postal_cruise_missile"
    ]
    registry_path = _write_registry(tmp_path, records)

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["missing_expansion_mechanics"] == [
        {
            "postal_effect": "cruise_missile",
            "registry_id": "nw_postal_cruise_missile",
        }
    ]


def test_validate_rules_reports_unexpected_expansion_registry_record(
    tmp_path: Path,
) -> None:
    records = _registry_records()
    cruise = next(
        record for record in records if record["id"] == "nw_postal_cruise_missile"
    )
    cruise["postal_effect"] = "unknown_mechanic"
    registry_path = _write_registry(tmp_path, records)

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["unexpected_expansion_mechanics"] == [
        {
            "postal_effect": "unknown_mechanic",
            "registry_id": "nw_postal_cruise_missile",
        }
    ]


def test_validate_rules_requires_cataloged_registry_id(tmp_path: Path) -> None:
    records = _registry_records()
    cruise = next(
        record for record in records if record["id"] == "nw_postal_cruise_missile"
    )
    cruise["id"] = "nw_postal_cruise_missile_alias"
    registry_path = _write_registry(tmp_path, records)

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["missing_expansion_mechanics"] == [
        {
            "postal_effect": "cruise_missile",
            "registry_id": "nw_postal_cruise_missile",
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
