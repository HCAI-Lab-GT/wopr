"""Source blocker report tests."""

from __future__ import annotations

from nuclear_war_env import source_blockers

EXPECTED_BLOCKERS = {
    "card_effect_transcription",
    "expansion_deck_composition",
    "expansion_rules_verification",
    "classic_spinner_edition",
    "nuclear_destruction_modern",
    "press_adjudication",
}


def test_source_blocker_payload_reports_known_remaining_gates() -> None:
    payload = source_blockers.source_blocker_payload()

    assert {item["blocker_id"] for item in payload} == EXPECTED_BLOCKERS
    assert {
        item["blocker_id"] for item in payload if item["category"] == "variant"
    } >= {"classic_spinner_edition", "nuclear_destruction_modern"}


def test_source_blocker_payload_has_required_fields() -> None:
    payload = source_blockers.source_blocker_payload()

    for item in payload:
        assert set(item) == {
            "blocker_id",
            "category",
            "description",
            "required_evidence",
        }
        assert isinstance(item["blocker_id"], str)
        assert isinstance(item["category"], str)
        assert isinstance(item["description"], str)
        assert isinstance(item["required_evidence"], list)
        assert all(isinstance(entry, str) for entry in item["required_evidence"])
        assert item["required_evidence"]


def test_rules_trace_blocker_is_resolved_by_semantic_trace() -> None:
    payload = source_blockers.source_blocker_payload()

    assert "rules_trace" not in {item["blocker_id"] for item in payload}
