"""Source evidence coverage reporting tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from nuclear_war_env.cards_registry import load_card_registry
from nuclear_war_env.expansions import EXPANSION_MECHANICS
from nuclear_war_env.rules import RULES_PATH
from nuclear_war_env.source_evidence_coverage import (
    card_effect_evidence_coverage,
    expansion_composition_evidence_coverage,
)


def test_missing_card_effect_manifest_reports_all_targets_missing(
    tmp_path: Path,
) -> None:
    registry = load_card_registry(RULES_PATH)
    expected_ids = tuple(
        record.identifier for record in registry.values() if record.count > 0
    )

    coverage = card_effect_evidence_coverage(tmp_path / "missing.jsonl")

    assert coverage.to_payload() == {
        "target_count": len(expected_ids),
        "required_ids": list(expected_ids),
        "recorded_count": 0,
        "recorded_ids": [],
        "verified_count": 0,
        "verified_ids": [],
        "missing_ids": list(expected_ids),
        "unverified_ids": [],
    }


def test_card_effect_coverage_separates_recorded_and_verified(
    tmp_path: Path,
) -> None:
    draft_id = "nw_base_b6794c74"
    verified_id = "nw_base_25ca25d8"
    path = _write_jsonl(
        tmp_path / "card_effects.jsonl",
        _card_entry(draft_id, "draft", False),
        _card_entry(verified_id, "second_pass_verified", True),
    )

    payload = card_effect_evidence_coverage(path).to_payload()

    assert payload["recorded_count"] == 2
    assert payload["recorded_ids"] == [draft_id, verified_id]
    assert payload["verified_count"] == 1
    assert payload["verified_ids"] == [verified_id]
    assert draft_id in cast("list[str]", payload["unverified_ids"])
    assert verified_id not in cast("list[str]", payload["missing_ids"])


def test_expansion_coverage_uses_expansion_catalog(tmp_path: Path) -> None:
    registry_id = "nw_postal_cruise_missile"
    path = _write_jsonl(
        tmp_path / "expansion.jsonl",
        _expansion_entry(registry_id, "second_pass_verified", True),
    )

    payload = expansion_composition_evidence_coverage(path).to_payload()

    assert payload["target_count"] == len(EXPANSION_MECHANICS)
    assert payload["recorded_ids"] == [registry_id]
    assert payload["verified_ids"] == [registry_id]
    assert registry_id not in cast("list[str]", payload["missing_ids"])
    assert payload["unverified_ids"] == []


def _card_entry(
    card_id: str,
    verification_status: str,
    verified_by_second_pass: bool,
) -> dict[str, object]:
    return {
        "card_id": card_id,
        "card_name": "source target",
        "card_type": "secret",
        "count": 1,
        "effect_summary": "Derived public-safe summary.",
        "evidence_kind": "physical_copy",
        "source_photo_or_file": "private/source-target.jpg",
        "verification_status": verification_status,
        "verified_by_second_pass": verified_by_second_pass,
    }


def _expansion_entry(
    registry_id: str,
    verification_status: str,
    verified_by_second_pass: bool,
) -> dict[str, object]:
    return {
        "registry_id": registry_id,
        "card_name": "Expansion target",
        "expansion_set": "Nuclear Proliferation",
        "count_in_deck": 1,
        "evidence_kind": "physical_copy",
        "source_reference": "private/expansion-target.jpg",
        "verification_status": verification_status,
        "verified_by_second_pass": verified_by_second_pass,
    }


def _write_jsonl(path: Path, *entries: dict[str, object]) -> Path:
    lines = [json.dumps(entry, sort_keys=True) for entry in entries]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
