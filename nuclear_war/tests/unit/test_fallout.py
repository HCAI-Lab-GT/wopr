"""Unit tests for fallout spinner helpers."""

from __future__ import annotations

from nuclear_war_env.fallout import (
    RADIOACTIVE_FALLOUT_DIE_TABLE_ID,
    SpinnerEffect,
    is_fallout_cloud,
    resolve_spinner,
    roll_fallout_die,
    roll_nuke_die,
    spin_spinner,
)
from nuclear_war_env.rng import SeededRNG


def test_resolve_spinner_boundaries() -> None:
    assert resolve_spinner(0).effect is SpinnerEffect.BOOSTER_EXPLODES
    assert resolve_spinner(5).effect is SpinnerEffect.DUD
    assert resolve_spinner(94).yield_multiplier == 2
    assert resolve_spinner(99).yield_multiplier == 3


def test_resolve_spinner_target_deltas() -> None:
    assert resolve_spinner(12).target_delta == -2
    assert resolve_spinner(30).target_delta == 1
    assert resolve_spinner(80).target_delta == 10


def test_spin_spinner_uses_rng() -> None:
    rng = SeededRNG(seed=123)
    roll_a, outcome_a = spin_spinner(rng)
    rng = SeededRNG(seed=123)
    roll_b, outcome_b = spin_spinner(rng)
    assert roll_a == roll_b
    assert outcome_a == outcome_b


def test_roll_nuke_die_postal_adjustment() -> None:
    rng = SeededRNG(seed=7)
    results = [roll_nuke_die(rng, postal_adjustment=True) for _ in range(20)]
    assert 6 not in results
    assert 2 not in results
    assert all(1 <= value <= 6 for value in results)


def test_roll_fallout_die_is_uniform_d6() -> None:
    # The postal Radioactive Fallout die is a plain uniform d6 (faces cloud,2-6).
    # Unlike the postal-adjusted nuke die, it keeps every face including 2 and 6.
    rng = SeededRNG(seed=7)
    results = [roll_fallout_die(rng) for _ in range(600)]
    assert set(results) == {1, 2, 3, 4, 5, 6}


def test_roll_fallout_die_is_deterministic_per_seed() -> None:
    first = [roll_fallout_die(SeededRNG(seed=41)) for _ in range(1)]
    second = [roll_fallout_die(SeededRNG(seed=41)) for _ in range(1)]
    assert first == second == [4]


def test_is_fallout_cloud_only_for_one() -> None:
    assert is_fallout_cloud(1) is True
    assert all(is_fallout_cloud(face) is False for face in (2, 3, 4, 5, 6))


def test_fallout_die_table_id_is_postal_radioactive() -> None:
    assert RADIOACTIVE_FALLOUT_DIE_TABLE_ID == "postal_radioactive_fallout_die"
