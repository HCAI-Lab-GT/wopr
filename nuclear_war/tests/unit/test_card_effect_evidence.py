"""Card-effect source evidence manifest tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.card_effect_evidence import validate_card_effect_evidence_manifest


def test_card_effect_evidence_manifest_reports_missing_file(tmp_path: Path) -> None:
    path = tmp_path / "missing.jsonl"

    result = validate_card_effect_evidence_manifest(path)

    assert result.to_payload() == {
        "path": str(path),
        "status": "missing",
        "record_count": 0,
        "verified_record_count": 0,
        "errors": [],
    }


def test_card_effect_evidence_manifest_accepts_verified_entry(tmp_path: Path) -> None:
    path = _write_manifest(tmp_path, _valid_entry())

    result = validate_card_effect_evidence_manifest(path)

    assert result.to_payload() == {
        "path": str(path),
        "status": "present",
        "record_count": 1,
        "verified_record_count": 1,
        "errors": [],
    }


def test_card_effect_evidence_manifest_rejects_malformed_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "card_effect_evidence.jsonl"
    path.write_text("{not json}\n", encoding="utf-8")

    result = validate_card_effect_evidence_manifest(path)

    assert result.errors == [{"line": "1", "error": "malformed_json"}]


def test_manifest_requires_public_safe_fields(tmp_path: Path) -> None:
    entry = _valid_entry()
    entry.pop("card_name")
    entry["count"] = 0
    entry["evidence_kind"] = "community_summary"
    entry["verification_status"] = "complete"
    path = _write_manifest(tmp_path, entry)

    result = validate_card_effect_evidence_manifest(path)

    assert result.errors == [
        _field_error("card_name", "missing_required"),
        _field_error("count", "invalid_count"),
        _field_error("evidence_kind", "invalid_value"),
        _field_error("verification_status", "invalid_value"),
    ]


def test_manifest_requires_second_pass_boolean(tmp_path: Path) -> None:
    entry = _valid_entry()
    entry["verified_by_second_pass"] = False
    path = _write_manifest(tmp_path, entry)

    result = validate_card_effect_evidence_manifest(path)

    assert result.errors == [
        {
            "line": "1",
            "card_id": "nw_base_b6794c74",
            "field": "verified_by_second_pass",
            "error": "second_pass_required",
        }
    ]


def test_manifest_rejects_duplicate_card_ids(tmp_path: Path) -> None:
    path = _write_manifest(tmp_path, _valid_entry(), _valid_entry())

    result = validate_card_effect_evidence_manifest(path)

    assert result.errors == [
        {
            "line": "2",
            "card_id": "nw_base_b6794c74",
            "error": "duplicate_card_id",
            "first_line": "1",
        }
    ]


def test_manifest_rejects_exact_text_fields(tmp_path: Path) -> None:
    entry = _valid_entry()
    entry["exact_text"] = "private card text"
    path = _write_manifest(tmp_path, entry)

    result = validate_card_effect_evidence_manifest(path)

    assert result.errors == [
        {
            "line": "1",
            "card_id": "nw_base_b6794c74",
            "field": "exact_text",
            "error": "restricted_field",
        }
    ]


def _valid_entry() -> dict[str, object]:
    return {
        "card_id": "nw_base_b6794c74",
        "card_name": "Test Ban",
        "card_type": "secret",
        "count": 1,
        "evidence_kind": "physical_copy",
        "effect_summary": "Target loses one turn.",
        "source_photo_or_file": "private/test-ban-front.jpg",
        "verification_status": "second_pass_verified",
        "verified_by_second_pass": True,
    }


def _write_manifest(tmp_path: Path, *entries: dict[str, object]) -> Path:
    path = tmp_path / "card_effect_evidence.jsonl"
    path.write_text(
        "\n".join(json.dumps(entry, sort_keys=True) for entry in entries),
        encoding="utf-8",
    )
    return path


def _field_error(field: str, error: str) -> dict[str, str]:
    return {
        "line": "1",
        "card_id": "nw_base_b6794c74",
        "field": field,
        "error": error,
    }
