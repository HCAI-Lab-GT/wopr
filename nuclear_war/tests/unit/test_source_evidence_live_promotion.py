"""Live source-evidence promotion boundary tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.rules import validate_rules


def test_validate_rules_rejects_draft_card_effect_live_manifest(
    tmp_path: Path,
) -> None:
    path = _write_jsonl(tmp_path / "card_effect_evidence.jsonl", _card_entry())

    payload = validate_rules(card_effect_evidence_path=path)

    assert payload["ok"] is False
    assert payload["card_effect_evidence_manifest_errors"] == []
    assert payload["card_effect_evidence_promotion_errors"] == [
        {
            "line": "1",
            "card_id": "nw_base_b6794c74",
            "field": "verification_status",
            "error": "live_manifest_requires_second_pass_verified",
        }
    ]


def test_validate_rules_rejects_draft_expansion_live_manifest(
    tmp_path: Path,
) -> None:
    path = _write_jsonl(
        tmp_path / "expansion_deck_composition.jsonl",
        _expansion_entry(),
    )

    payload = validate_rules(expansion_composition_evidence_path=path)

    assert payload["ok"] is False
    assert payload["expansion_composition_evidence_manifest_errors"] == []
    assert payload["expansion_composition_evidence_promotion_errors"] == [
        {
            "line": "1",
            "registry_id": "nw_postal_cruise_missile",
            "field": "verification_status",
            "error": "live_manifest_requires_second_pass_verified",
        }
    ]


def test_validate_rules_reports_no_promotion_errors_for_missing_manifests() -> None:
    payload = validate_rules()

    assert payload["ok"] is True
    assert payload["card_effect_evidence_promotion_errors"] == []
    assert payload["expansion_composition_evidence_promotion_errors"] == []


def _card_entry() -> dict[str, object]:
    return {
        "card_id": "nw_base_b6794c74",
        "card_name": "Test Ban",
        "card_type": "secret",
        "count": 1,
        "effect_summary": "Target loses one turn.",
        "evidence_kind": "physical_copy",
        "source_photo_or_file": "private/test-ban-front.jpg",
        "verification_status": "draft",
        "verified_by_second_pass": False,
    }


def _expansion_entry() -> dict[str, object]:
    return {
        "registry_id": "nw_postal_cruise_missile",
        "card_name": "Cruise Missile",
        "expansion_set": "Nuclear Proliferation",
        "count_in_deck": 1,
        "evidence_kind": "physical_copy",
        "source_reference": "private/proliferation-counts.csv",
        "verification_status": "draft",
        "verified_by_second_pass": False,
    }


def _write_jsonl(path: Path, entry: dict[str, object]) -> Path:
    path.write_text(json.dumps(entry, sort_keys=True), encoding="utf-8")
    return path
