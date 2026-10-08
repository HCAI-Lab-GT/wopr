"""Variant acceptance documentation tests."""

from __future__ import annotations

from pathlib import Path

from nuclear_war_env.variant_catalog import known_variant_ids


def test_variant_acceptance_doc_covers_known_variants() -> None:
    path = Path("docs/variant_acceptance.md")

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "Deferred variants remain rejected" in text
    for variant_id in known_variant_ids():
        assert f"## {variant_id}" in text
