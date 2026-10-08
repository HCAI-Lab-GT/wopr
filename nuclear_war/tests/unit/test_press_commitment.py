"""Full-press commitment parsing tests."""

from __future__ import annotations

import pytest

from nuclear_war_concordia.press_commitment import parse_commitment


def test_parse_commitment_returns_none_for_absent() -> None:
    assert parse_commitment(None) is None


def test_parse_commitment_reads_kind_only() -> None:
    assert parse_commitment({"kind": "stand_down"}) == {"kind": "stand_down"}


def test_parse_commitment_reads_full_object() -> None:
    commitment = {"kind": "stand_down", "target_round": 3, "notes": "no launch"}

    assert parse_commitment(commitment) == commitment


@pytest.mark.parametrize(
    "payload",
    [
        {"kind": ""},
        {"kind": "   "},
        {"kind": 5},
        {"target_round": 3},
        "not a dict",
        {"kind": "stand_down", "extra": 1},
        {"kind": "stand_down", "target_round": "3"},
        {"kind": "stand_down", "target_round": 2.0},
        {"kind": "stand_down", "target_round": 0},
        {"kind": "stand_down", "target_round": -1},
        {"kind": "stand_down", "target_round": True},
    ],
)
def test_parse_commitment_rejects_invalid(payload) -> None:
    assert parse_commitment(payload) is None


def test_parse_commitment_allows_kind_without_optional_fields() -> None:
    result = parse_commitment({"kind": "no_first_use"})

    assert result == {"kind": "no_first_use"}


def test_parse_commitment_allows_kind_with_notes_only() -> None:
    result = parse_commitment({"kind": "ally_with", "notes": "coordinate"})

    assert result == {"kind": "ally_with", "notes": "coordinate"}
