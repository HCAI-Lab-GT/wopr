"""Rule validation tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from nuclear_war_env.rules import RULES_PATH, validate_rules


def test_validate_rules_reports_supported_effect_coverage() -> None:
    payload = validate_rules()
    assert payload["ok"] is True
    assert payload["unsupported_effect_keys"] == []
    assert payload["restricted_text_fields"] == []
    assert set(payload["supported_effect_keys"]) >= {
        "damage_population_millions",
        "gain_from_bank_millions",
        "remove_to_bank_millions",
        "steal_population_millions",
        "target_loses_turns",
    }


def test_validate_rules_requires_postal_special_registry_records() -> None:
    payload = validate_rules()
    assert payload["missing_postal_special_effects"] == []
    assert payload["metadata_records_in_deck"] == []
    assert set(payload["postal_special_effects"]) >= {
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


def test_validate_rules_reports_active_edition_variant() -> None:
    payload = validate_rules()
    assert payload["active_variant"] == {
        "variant_id": "base_later_two_d10",
        "hand_draw_target": 10,
        "population_deck_size": 40,
        "randomizer": "base_two_d10_fallout_chart",
        "initial_face_down_cards": 2,
        "anti_missile_turn_jump": True,
        "expansion_sets": [],
        "special_powers_enabled": False,
        "trading_enabled": False,
        "press_enabled": False,
        "simultaneous_orders": False,
    }


def test_validate_rules_reports_no_unresolved_source_labels() -> None:
    payload = validate_rules()
    assert payload["unresolved_source_labels"] == []


def test_validate_rules_reports_source_evidence_and_confidence() -> None:
    payload = validate_rules()
    assert payload["missing_source_fields"] == []
    assert payload["missing_confidence_fields"] == []
    assert payload["invalid_confidence_fields"] == []


def test_validate_rules_reports_missing_card_effect_evidence_manifest() -> None:
    payload = validate_rules()

    assert payload["ok"] is True
    assert payload["card_effect_evidence_manifest"]["status"] == "missing"
    assert payload["card_effect_evidence_manifest"]["record_count"] == 0
    assert payload["card_effect_evidence_manifest_errors"] == []
    assert payload["card_effect_evidence_coverage"]["recorded_count"] == 0
    assert payload["card_effect_evidence_coverage"]["verified_count"] == 0
    assert payload["card_effect_evidence_coverage"]["missing_ids"]
    assert payload["expansion_composition_evidence_coverage"]["recorded_count"] == 0
    assert payload["expansion_composition_evidence_coverage"]["verified_count"] == 0
    assert payload["expansion_composition_evidence_coverage"]["missing_ids"]


def test_validate_rules_fails_invalid_card_effect_evidence_manifest(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "card_effect_evidence.jsonl"
    evidence_path.write_text(
        json.dumps(
            {
                "card_id": "nw_base_b6794c74",
                "card_name": "Test Ban",
                "card_type": "secret",
                "count": 1,
                "evidence_kind": "physical_copy",
                "effect_summary": "Target loses one turn.",
                "source_photo_or_file": "private/test-ban-front.jpg",
                "verification_status": "second_pass_verified",
                "verified_by_second_pass": True,
                "exact_text": "private card text",
            }
        ),
        encoding="utf-8",
    )

    payload = validate_rules(card_effect_evidence_path=evidence_path)

    assert payload["ok"] is False
    assert payload["card_effect_evidence_manifest_errors"] == [
        {
            "line": "1",
            "card_id": "nw_base_b6794c74",
            "field": "exact_text",
            "error": "restricted_field",
        }
    ]


def test_validate_rules_reports_source_index_coverage() -> None:
    payload = validate_rules()
    assert payload["source_index_id_count"] >= 30


def test_validate_rules_rejects_invalid_confidence_values(tmp_path: Path) -> None:
    records = _registry_records()
    records[0]["confidence"] = "uncertain"
    registry_path = _write_registry(tmp_path, records)

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["invalid_confidence_fields"] == [
        {"card_id": records[0]["id"], "confidence": "uncertain"}
    ]


@pytest.mark.parametrize("count_in_deck", ["1", True, -1])
def test_validate_rules_rejects_invalid_count_values(
    tmp_path: Path, count_in_deck: object
) -> None:
    records = _registry_records()
    records[0]["count_in_deck"] = count_in_deck
    registry_path = _write_registry(tmp_path, records)

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["invalid_count_fields"] == [
        {"card_id": records[0]["id"], "count_in_deck": count_in_deck}
    ]


@pytest.mark.parametrize("count_in_deck", [1, True])
def test_validate_rules_rejects_metadata_records_in_base_deck(
    tmp_path: Path, count_in_deck: object
) -> None:
    records = _registry_records()
    metadata_record = next(
        record
        for record in records
        if record.get("registry_status") == "rules_metadata_only"
    )
    metadata_record["count_in_deck"] = count_in_deck
    registry_path = _write_registry(tmp_path, records)

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["metadata_records_in_deck"] == [
        {"card_id": metadata_record["id"], "count_in_deck": count_in_deck}
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
