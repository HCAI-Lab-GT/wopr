"""CLI source-evidence draft stub export tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.cli import main


def test_cli_source_evidence_draft_stubs_outputs_card_effect_jsonl(
    capsys,
) -> None:
    code = main(["source-evidence-draft-stubs", "--kind", "card-effects"])

    captured = capsys.readouterr()
    records = _jsonl_records(captured.out)
    assert code == 0
    assert len(records) == 30
    assert records[0]["card_id"] == "nw_base_f135174f"
    assert records[0]["verification_status"] == "draft"
    assert records[0]["verified_by_second_pass"] is False


def test_cli_source_evidence_draft_stubs_outputs_expansion_jsonl(
    capsys,
) -> None:
    code = main(["source-evidence-draft-stubs", "--kind", "expansion-composition"])

    captured = capsys.readouterr()
    records = _jsonl_records(captured.out)
    assert code == 0
    assert len(records) == 10
    assert records[0]["registry_id"] == "nw_postal_atomic_cannon"
    assert records[0]["verification_status"] == "draft"
    assert records[0]["verified_by_second_pass"] is False


def test_cli_source_evidence_draft_stubs_can_feed_preflight(
    tmp_path: Path,
    capsys,
) -> None:
    code = main(["source-evidence-draft-stubs", "--kind", "card-effects"])
    card_effects = tmp_path / "card_effects.draft.jsonl"
    card_effects.write_text(capsys.readouterr().out, encoding="utf-8")

    preflight_code = main(
        ["validate-source-evidence", "--card-effects", str(card_effects)]
    )

    payload = json.loads(capsys.readouterr().out)
    assert code == 0
    assert preflight_code == 0
    assert payload["card_effect_evidence_manifest"]["record_count"] == 30
    assert payload["card_effect_evidence_manifest"]["verified_record_count"] == 0


def _jsonl_records(text: str) -> list[dict[str, object]]:
    return [json.loads(line) for line in text.splitlines() if line]
