"""Source-evidence policy documentation tests."""

from __future__ import annotations

from pathlib import Path


def test_source_evidence_docs_track_current_capture_workflow() -> None:
    texts = [
        Path("docs/v1_source_evidence.md").read_text(encoding="utf-8"),
        Path("docs/source_research_policy.md").read_text(encoding="utf-8"),
    ]
    combined = "\n".join(texts)

    assert "validate-source-evidence" in combined
    assert "source-evidence-targets" in combined
    assert "source-evidence-draft-stubs" in combined
    assert "PUBLIC_SOURCE_LEADS.md" in combined
    assert "card_effect_evidence_target_details" in combined
    assert "expansion_composition_evidence_target_details" in combined
    assert "card_effect_evidence_coverage" in combined
    assert "expansion_composition_evidence_coverage" in combined
    assert "card_effect_evidence_promotion_errors" in combined
    assert "expansion_composition_evidence_promotion_errors" in combined
    assert "second-pass verified" in combined.lower()
