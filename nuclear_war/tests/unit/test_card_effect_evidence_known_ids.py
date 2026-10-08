"""Card-effect evidence known-id tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.card_effect_evidence import validate_card_effect_evidence_manifest
from nuclear_war_env.rules import validate_rules


def test_card_effect_evidence_rejects_unknown_card_id(tmp_path: Path) -> None:
    entry = _card_effect_entry()
    entry["card_id"] = "nw_missing_card"
    path = _write_manifest(tmp_path, entry)

    result = validate_card_effect_evidence_manifest(
        path,
        known_card_ids={"nw_base_b6794c74"},
    )

    assert result.errors == [
        {
            "line": "1",
            "card_id": "nw_missing_card",
            "field": "card_id",
            "error": "unknown_card_id",
        }
    ]


def test_validate_rules_fails_unknown_card_effect_evidence_id(
    tmp_path: Path,
) -> None:
    entry = _card_effect_entry()
    entry["card_id"] = "nw_missing_card"
    path = _write_manifest(tmp_path, entry)

    payload = validate_rules(card_effect_evidence_path=path)

    assert payload["ok"] is False
    assert payload["card_effect_evidence_manifest_errors"] == [
        {
            "line": "1",
            "card_id": "nw_missing_card",
            "field": "card_id",
            "error": "unknown_card_id",
        }
    ]


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


def _write_manifest(tmp_path: Path, *entries: dict[str, object]) -> Path:
    path = tmp_path / "card_effect_evidence.jsonl"
    path.write_text(
        "\n".join(json.dumps(entry, sort_keys=True) for entry in entries),
        encoding="utf-8",
    )
    return path
