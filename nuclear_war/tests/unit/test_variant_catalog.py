"""Edition variant catalog validation tests."""

from __future__ import annotations

from nuclear_war_env import variant_catalog, variants
from nuclear_war_env.rules import validate_rules

EXPECTED_VARIANTS = {
    "base_later_two_d10",
    "classic_spinner_scan",
    "nuclear_destruction_modern",
    "postal_press",
    "no_press_house",
    "combined_expansions",
}


def test_variant_catalog_lists_known_edition_boundaries() -> None:
    payload = variant_catalog.variant_catalog_payload()

    assert {item["variant_id"] for item in payload} == EXPECTED_VARIANTS


def test_variant_catalog_has_exactly_one_active_entry() -> None:
    active = [
        item["variant_id"]
        for item in variant_catalog.variant_catalog_payload()
        if item["status"] == "active"
    ]

    assert active == [variants.ACTIVE_VARIANT_ID]


def test_variant_catalog_reports_missing_source_ids() -> None:
    gaps = variant_catalog.variant_catalog_gaps({"MIR-001"})

    assert {"variant_id": "classic_spinner_scan", "source_id": "MIR-002"} in gaps
    assert {
        "variant_id": "nuclear_destruction_modern",
        "source_id": "OFF-002",
    } in gaps


def test_validate_rules_reports_variant_catalog_boundaries() -> None:
    payload = validate_rules()

    assert {item["variant_id"] for item in payload["variant_catalog"]} == (
        EXPECTED_VARIANTS
    )
    assert payload["variant_catalog_gaps"] == []


def test_validate_requested_variant_accepts_active_variant() -> None:
    variant_catalog.validate_requested_variant(
        variants.ACTIVE_VARIANT_ID,
        "Simulation",
    )


def test_resolve_requested_variant_returns_active_variant() -> None:
    resolved = variant_catalog.resolve_requested_variant(
        variants.ACTIVE_VARIANT_ID,
        "Simulation",
    )

    assert resolved is variants.ACTIVE_VARIANT


def test_validate_requested_variant_rejects_non_string() -> None:
    try:
        variant_catalog.validate_requested_variant(0, "Simulation")
    except ValueError as error:
        assert str(error) == "Simulation variant_id must be a string"
    else:
        raise AssertionError("expected variant validation error")


def test_validate_requested_variant_rejects_unknown_variant() -> None:
    try:
        variant_catalog.validate_requested_variant("future_variant", "Simulation")
    except ValueError as error:
        assert str(error) == "Unknown variant: future_variant"
    else:
        raise AssertionError("expected variant validation error")


def test_validate_requested_variant_rejects_deferred_variant_with_blockers() -> None:
    try:
        variant_catalog.validate_requested_variant("classic_spinner_scan", "Simulation")
    except ValueError as error:
        message = str(error)
    else:
        raise AssertionError("expected variant validation error")

    assert "Simulation variant classic_spinner_scan is deferred" in message
    assert "spinner probabilities" in message


def test_resolve_requested_variant_rejects_deferred_variant_with_blockers() -> None:
    try:
        variant_catalog.resolve_requested_variant("classic_spinner_scan", "Setup")
    except ValueError as error:
        message = str(error)
    else:
        raise AssertionError("expected variant resolution error")

    assert "Setup variant classic_spinner_scan is deferred" in message
    assert "spinner probabilities" in message
