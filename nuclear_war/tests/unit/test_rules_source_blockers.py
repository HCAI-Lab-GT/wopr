"""Rule validation source-blocker report tests."""

from __future__ import annotations

from nuclear_war_env.rules import validate_rules


def test_validate_rules_reports_informational_source_blockers() -> None:
    payload = validate_rules()

    assert payload["ok"] is True
    assert {item["blocker_id"] for item in payload["source_blockers"]} >= {
        "card_effect_transcription",
        "expansion_deck_composition",
        "classic_spinner_edition",
        "press_adjudication",
    }
