"""Expansion deck-composition source evidence manifest tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env import expansion_composition_evidence as evidence


def test_manifest_reports_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "missing.jsonl"

    result = evidence.validate_expansion_composition_evidence_manifest(path)

    assert result.to_payload() == {
        "path": str(path),
        "status": "missing",
        "record_count": 0,
        "verified_record_count": 0,
        "errors": [],
    }


def test_manifest_accepts_verified_entry(tmp_path: Path) -> None:
    path = _write_manifest(tmp_path, _valid_entry())

    result = evidence.validate_expansion_composition_evidence_manifest(path)

    assert result.to_payload() == {
        "path": str(path),
        "status": "present",
        "record_count": 1,
        "verified_record_count": 1,
        "errors": [],
    }


def test_manifest_rejects_malformed_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "expansion_deck_composition.jsonl"
    path.write_text("{not json}\n", encoding="utf-8")

    result = evidence.validate_expansion_composition_evidence_manifest(path)

    assert result.errors == [{"line": "1", "error": "malformed_json"}]


def test_manifest_requires_public_safe_fields(tmp_path: Path) -> None:
    entry = _valid_entry()
    entry.pop("card_name")
    entry["count_in_deck"] = 0
    entry["evidence_kind"] = "community_summary"
    entry["verification_status"] = "complete"
    path = _write_manifest(tmp_path, entry)

    result = evidence.validate_expansion_composition_evidence_manifest(path)

    assert result.errors == [
        _field_error("card_name", "missing_required"),
        _field_error("count_in_deck", "invalid_count"),
        _field_error("evidence_kind", "invalid_value"),
        _field_error("verification_status", "invalid_value"),
    ]


def test_manifest_requires_known_registry_id(tmp_path: Path) -> None:
    entry = _valid_entry()
    entry["registry_id"] = "nw_unknown_expansion_card"
    path = _write_manifest(tmp_path, entry)

    result = evidence.validate_expansion_composition_evidence_manifest(path)

    assert result.errors == [
        {
            "line": "1",
            "registry_id": "nw_unknown_expansion_card",
            "field": "registry_id",
            "error": "unknown_registry_id",
        }
    ]


def test_manifest_requires_second_pass_boolean(tmp_path: Path) -> None:
    entry = _valid_entry()
    entry["verified_by_second_pass"] = False
    path = _write_manifest(tmp_path, entry)

    result = evidence.validate_expansion_composition_evidence_manifest(path)

    assert result.errors == [
        _field_error("verified_by_second_pass", "second_pass_required")
    ]


def test_manifest_rejects_duplicate_registry_ids(tmp_path: Path) -> None:
    path = _write_manifest(tmp_path, _valid_entry(), _valid_entry())

    result = evidence.validate_expansion_composition_evidence_manifest(path)

    assert result.errors == [
        {
            "line": "2",
            "registry_id": "nw_postal_cruise_missile",
            "error": "duplicate_registry_id",
            "first_line": "1",
        }
    ]


def test_manifest_rejects_exact_text_fields(tmp_path: Path) -> None:
    entry = _valid_entry()
    entry["exact_text"] = "private card text"
    path = _write_manifest(tmp_path, entry)

    result = evidence.validate_expansion_composition_evidence_manifest(path)

    assert result.errors == [_field_error("exact_text", "restricted_field")]


def _valid_entry() -> dict[str, object]:
    return {
        "registry_id": "nw_postal_cruise_missile",
        "card_name": "Cruise Missile",
        "expansion_set": "Nuclear Proliferation",
        "count_in_deck": 1,
        "evidence_kind": "physical_copy",
        "source_reference": "private/proliferation-counts.csv",
        "verification_status": "second_pass_verified",
        "verified_by_second_pass": True,
    }


def _write_manifest(tmp_path: Path, *entries: dict[str, object]) -> Path:
    path = tmp_path / "expansion_deck_composition.jsonl"
    path.write_text(
        "\n".join(json.dumps(entry, sort_keys=True) for entry in entries),
        encoding="utf-8",
    )
    return path


def _field_error(field: str, error: str) -> dict[str, str]:
    return {
        "line": "1",
        "registry_id": "nw_postal_cruise_missile",
        "field": field,
        "error": error,
    }
