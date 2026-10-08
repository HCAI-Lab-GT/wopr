"""CLI source-evidence preflight tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.cli import main


def test_cli_validate_source_evidence_accepts_draft_paths(
    tmp_path: Path,
    capsys,
) -> None:
    card_effects = _write_jsonl(tmp_path / "card_effects.jsonl", _card_entry())
    expansion = _write_jsonl(tmp_path / "expansion.jsonl", _expansion_entry())

    code = main(
        [
            "validate-source-evidence",
            "--card-effects",
            str(card_effects),
            "--expansion-composition",
            str(expansion),
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["ok"] is True
    assert payload["card_effect_evidence_manifest"]["record_count"] == 1
    assert payload["card_effect_evidence_manifest"]["verified_record_count"] == 0
    assert payload["card_effect_evidence_coverage"]["recorded_ids"] == [
        "nw_base_b6794c74"
    ]
    assert payload["card_effect_evidence_coverage"]["verified_ids"] == []
    assert (
        "nw_base_b6794c74" in payload["card_effect_evidence_coverage"]["unverified_ids"]
    )
    assert payload["expansion_composition_evidence_manifest"]["record_count"] == 1
    assert payload["expansion_composition_evidence_manifest_errors"] == []
    assert payload["expansion_composition_evidence_coverage"]["recorded_ids"] == [
        "nw_postal_cruise_missile"
    ]
    assert payload["expansion_composition_evidence_coverage"]["verified_ids"] == []
    assert (
        "nw_postal_cruise_missile"
        in payload["expansion_composition_evidence_coverage"]["unverified_ids"]
    )
    assert "card_effect_evidence_promotion_errors" not in payload
    assert "expansion_composition_evidence_promotion_errors" not in payload


def test_cli_validate_source_evidence_rejects_unknown_card_id(
    tmp_path: Path,
    capsys,
) -> None:
    entry = _card_entry()
    entry["card_id"] = "nw_missing_card"
    card_effects = _write_jsonl(tmp_path / "card_effects.jsonl", entry)

    code = main(
        [
            "validate-source-evidence",
            "--card-effects",
            str(card_effects),
        ]
    )

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 1
    assert payload["ok"] is False
    assert payload["card_effect_evidence_manifest_errors"] == [
        {
            "line": "1",
            "card_id": "nw_missing_card",
            "field": "card_id",
            "error": "unknown_card_id",
        }
    ]


def test_cli_validate_source_evidence_requires_a_path(capsys) -> None:
    code = main(["validate-source-evidence"])

    captured = capsys.readouterr()
    assert code == 2
    assert "At least one source evidence path is required" in captured.err


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
