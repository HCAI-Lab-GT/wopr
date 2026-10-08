"""Source evidence private reference tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.card_effect_evidence import (
    validate_card_effect_evidence_manifest,
)
from nuclear_war_env.expansion_composition_evidence import (
    validate_expansion_composition_evidence_manifest,
)


def test_physical_copy_card_effect_reference_must_be_private(
    tmp_path: Path,
) -> None:
    entry = _card_effect_entry()
    entry["source_photo_or_file"] = "captures/test-ban-front.jpg"
    path = _write_manifest(tmp_path, "card_effect_evidence.jsonl", entry)

    result = validate_card_effect_evidence_manifest(path)

    assert result.errors == [
        {
            "line": "1",
            "card_id": "nw_base_b6794c74",
            "field": "source_photo_or_file",
            "error": "non_private_physical_copy_reference",
        }
    ]


def test_publisher_card_effect_reference_can_be_non_private(
    tmp_path: Path,
) -> None:
    entry = _card_effect_entry()
    entry["evidence_kind"] = "publisher_authorized_source"
    entry["source_photo_or_file"] = "publisher-authorized/source-id"
    path = _write_manifest(tmp_path, "card_effect_evidence.jsonl", entry)

    result = validate_card_effect_evidence_manifest(path)

    assert result.errors == []


def test_physical_copy_expansion_reference_must_be_private(
    tmp_path: Path,
) -> None:
    entry = _expansion_entry()
    entry["source_reference"] = "captures/proliferation-counts.csv"
    path = _write_manifest(tmp_path, "expansion_deck_composition.jsonl", entry)

    result = validate_expansion_composition_evidence_manifest(path)

    assert result.errors == [
        {
            "line": "1",
            "registry_id": "nw_postal_cruise_missile",
            "field": "source_reference",
            "error": "non_private_physical_copy_reference",
        }
    ]


def test_publisher_expansion_reference_can_be_non_private(tmp_path: Path) -> None:
    entry = _expansion_entry()
    entry["evidence_kind"] = "publisher_authorized_source"
    entry["source_reference"] = "publisher-authorized/source-id"
    path = _write_manifest(tmp_path, "expansion_deck_composition.jsonl", entry)

    result = validate_expansion_composition_evidence_manifest(path)

    assert result.errors == []


def _card_effect_entry() -> dict[str, object]:
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


def _expansion_entry() -> dict[str, object]:
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


def _write_manifest(
    tmp_path: Path,
    name: str,
    *entries: dict[str, object],
) -> Path:
    path = tmp_path / name
    path.write_text(
        "\n".join(json.dumps(entry, sort_keys=True) for entry in entries),
        encoding="utf-8",
    )
    return path
