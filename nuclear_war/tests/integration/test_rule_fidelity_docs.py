"""Rule fidelity documentation tests."""

from __future__ import annotations

from pathlib import Path


def test_rule_fidelity_matrix_tracks_active_population_deck_model() -> None:
    text = Path("docs/rule_fidelity_matrix.md").read_text(encoding="utf-8")

    assert "population deck size model 40 cards" in text
    assert "population deck size model 20 cards" not in text
