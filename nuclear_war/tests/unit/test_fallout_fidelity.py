"""Fidelity lock: the spinner/fallout table must match the documented two-d10
fallout chart (research bundle 04_simulation_model/spinner_and_die_tables.json).

This guards the gameplay-critical damage model against drift from the source.
"""

from __future__ import annotations

import pytest

from nuclear_war_env.fallout import SpinnerEffect, resolve_spinner

# (roll, effect, target_delta, yield_multiplier, attacker_backfire) per the
# documented base_two_d10_fallout_chart. Roll is a representative value in range.
_CHART = [
    (2, SpinnerEffect.BOOSTER_EXPLODES, 0, 0, True),  # 00-04 booster/out-of-fuel
    (7, SpinnerEffect.DUD, 0, 0, False),  # 05-09 dud
    (15, SpinnerEffect.SHELTER_SAVES, -2, 1, False),  # 10-22 shelter saves 2M
    (30, SpinnerEffect.FIREBALL, 1, 1, False),  # 23-35 fireball +1M
    (40, SpinnerEffect.NO_RADIATION, 0, 1, False),  # 36-49 no fallout
    (55, SpinnerEffect.FALLOUT_2M, 2, 1, False),  # 50-63 +2M
    (70, SpinnerEffect.FALLOUT_5M, 5, 1, False),  # 64-76 +5M
    (80, SpinnerEffect.FALLOUT_10M, 10, 1, False),  # 77-89 +10M
    (92, SpinnerEffect.DIRTY_BOMB, 0, 2, False),  # 90-94 double yield
    (97, SpinnerEffect.STOCKPILE_EXPLODES, 0, 3, False),  # 95-99 triple yield
]


@pytest.mark.parametrize("roll,effect,target_delta,yield_multiplier,backfire", _CHART)
def test_spinner_matches_documented_chart(
    roll: int,
    effect: SpinnerEffect,
    target_delta: int,
    yield_multiplier: int,
    backfire: bool,
) -> None:
    outcome = resolve_spinner(roll)
    assert outcome.effect is effect
    assert outcome.target_delta == target_delta
    assert outcome.yield_multiplier == yield_multiplier
    assert outcome.attacker_backfire is backfire


def test_chart_covers_every_roll_0_to_99() -> None:
    # No gaps or overlaps: every two-d10 roll resolves to exactly one outcome.
    for roll in range(100):
        resolve_spinner(roll)  # raises if any roll is uncovered
