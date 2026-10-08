"""Expansion composition validate-rules integration tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.rules import validate_rules


def test_validate_rules_reports_missing_expansion_composition_manifest() -> None:
    payload = validate_rules()

    assert payload["ok"] is True
    assert payload["expansion_composition_evidence_manifest"]["status"] == "missing"
    assert payload["expansion_composition_evidence_manifest"]["record_count"] == 0
    assert payload["expansion_composition_evidence_manifest_errors"] == []


def test_validate_rules_fails_invalid_expansion_composition_manifest(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "expansion_deck_composition.jsonl"
    evidence_path.write_text(
        json.dumps(
            {
                "registry_id": "nw_postal_cruise_missile",
                "card_name": "Cruise Missile",
                "expansion_set": "Nuclear Proliferation",
                "count_in_deck": 1,
                "evidence_kind": "physical_copy",
                "source_reference": "private/proliferation-counts.csv",
                "verification_status": "second_pass_verified",
                "verified_by_second_pass": True,
                "exact_text": "private card text",
            }
        ),
        encoding="utf-8",
    )

    payload = validate_rules(expansion_composition_evidence_path=evidence_path)

    assert payload["ok"] is False
    assert payload["expansion_composition_evidence_manifest_errors"] == [
        {
            "line": "1",
            "registry_id": "nw_postal_cruise_missile",
            "field": "exact_text",
            "error": "restricted_field",
        }
    ]
