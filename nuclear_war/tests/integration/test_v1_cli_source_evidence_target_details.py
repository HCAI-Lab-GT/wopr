"""CLI source-evidence target detail tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.cli import main


def test_cli_validate_source_evidence_reports_target_details(
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
    assert payload["card_effect_evidence_target_details"]["unverified_targets"] == [
        {
            "card_id": "nw_base_b6794c74",
            "card_name": "Test Ban",
            "card_type": "secret",
            "count": 1,
        }
    ]
    assert payload["expansion_composition_evidence_target_details"][
        "unverified_targets"
    ] == [
        {
            "registry_id": "nw_postal_cruise_missile",
            "postal_effect": "cruise_missile",
            "supported_modes": ["postal"],
        }
    ]
    assert (
        payload["card_effect_evidence_target_details"]["missing_targets"][0][
            "card_name"
        ]
        == "Warhead 10 Mt"
    )
    assert "source_photo_or_file" not in captured.out
    assert "source_reference" not in captured.out
    assert "private/test-ban-front.jpg" not in captured.out
    assert "private/proliferation-counts.csv" not in captured.out
    assert "Target loses one turn." not in captured.out


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
