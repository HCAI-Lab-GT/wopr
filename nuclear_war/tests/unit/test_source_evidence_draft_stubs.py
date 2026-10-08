"""Source evidence draft stub export tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.card_effect_evidence import (
    validate_card_effect_evidence_manifest,
)
from nuclear_war_env.cards_registry import load_card_registry
from nuclear_war_env.expansion_composition_evidence import (
    validate_expansion_composition_evidence_manifest,
)
from nuclear_war_env.rules import RULES_PATH
from nuclear_war_env.source_evidence_draft_stubs import (
    card_effect_draft_stub_jsonl,
    expansion_composition_draft_stub_jsonl,
)


def test_card_effect_draft_stubs_validate_as_public_safe_drafts(
    tmp_path: Path,
) -> None:
    registry = load_card_registry(RULES_PATH)
    path = tmp_path / "card_effects.draft.jsonl"
    path.write_text(card_effect_draft_stub_jsonl(), encoding="utf-8")

    result = validate_card_effect_evidence_manifest(
        path,
        known_card_ids=set(registry),
    )
    records = _jsonl_records(path)

    assert result.status == "present"
    assert result.record_count == 30
    assert result.verified_record_count == 0
    assert result.errors == []
    assert records[0]["card_id"] == "nw_base_f135174f"
    assert records[0]["effect_summary"] == "TODO derived effect summary"
    source_photo = records[0]["source_photo_or_file"]
    assert isinstance(source_photo, str)
    assert source_photo.startswith("private/")
    assert "exact_text" not in str(records).lower()


def test_expansion_composition_draft_stubs_validate_as_public_safe_drafts(
    tmp_path: Path,
) -> None:
    path = tmp_path / "expansion.draft.jsonl"
    path.write_text(expansion_composition_draft_stub_jsonl(), encoding="utf-8")

    result = validate_expansion_composition_evidence_manifest(path)
    records = _jsonl_records(path)

    assert result.status == "present"
    assert result.record_count == 10
    assert result.verified_record_count == 0
    assert result.errors == []
    assert records[0]["registry_id"] == "nw_postal_atomic_cannon"
    assert records[0]["expansion_set"] == "TODO expansion set from source"
    source_reference = records[0]["source_reference"]
    assert isinstance(source_reference, str)
    assert source_reference.startswith("private/")
    assert "official_text" not in str(records).lower()


def _jsonl_records(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]
