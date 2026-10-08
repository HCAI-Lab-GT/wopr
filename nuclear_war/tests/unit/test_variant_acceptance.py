"""Variant acceptance criteria tests."""

from __future__ import annotations

from nuclear_war_env import variant_catalog


def test_variant_catalog_entries_report_acceptance_criteria() -> None:
    payload = variant_catalog.variant_catalog_payload()

    for item in payload:
        assert isinstance(item["acceptance_criteria"], list)
        assert item["acceptance_criteria"]
        assert all(isinstance(entry, str) for entry in item["acceptance_criteria"])


def test_variant_catalog_reports_active_and_deferred_acceptance_criteria() -> None:
    payload = _criteria_by_variant()

    assert {
        "10-card hand draw target verified",
        "40-card population deck verified",
        "two-d10 fallout chart verified",
        "no press or expansion behavior enabled",
    } <= payload["base_later_two_d10"]
    assert {
        "spinner probabilities transcribed",
        "9-card hand model verified",
    } <= payload["classic_spinner_scan"]
    assert {
        "ND deck composition verified",
        "Nuclear Escalation die rules verified",
        "six-player mat rules verified",
    } <= payload["nuclear_destruction_modern"]


def _criteria_by_variant() -> dict[str, set[str]]:
    payload: dict[str, set[str]] = {}
    for item in variant_catalog.variant_catalog_payload():
        variant_id = item["variant_id"]
        criteria = item["acceptance_criteria"]
        assert isinstance(variant_id, str)
        assert isinstance(criteria, list)
        assert all(isinstance(entry, str) for entry in criteria)
        payload[variant_id] = set(criteria)
    return payload
