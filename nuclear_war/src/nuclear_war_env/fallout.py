"""Fallout spinner and nuke die helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .rng import SeededRNG


class SpinnerEffect(StrEnum):
    BOOSTER_EXPLODES = "booster_explodes"
    DUD = "dud"
    SHELTER_SAVES = "shelter_saves"
    FIREBALL = "fireball"
    NO_RADIATION = "no_radiation"
    FALLOUT_2M = "fallout_2m"
    FALLOUT_5M = "fallout_5m"
    FALLOUT_10M = "fallout_10m"
    DIRTY_BOMB = "dirty_bomb"
    STOCKPILE_EXPLODES = "stockpile_explodes"


@dataclass(frozen=True)
class FalloutOutcome:
    effect: SpinnerEffect
    target_delta: int = 0
    attacker_backfire: bool = False
    yield_multiplier: int = 1


_SPINNER_TABLE: list[tuple[range, FalloutOutcome]] = [
    (
        range(0, 5),
        FalloutOutcome(
            SpinnerEffect.BOOSTER_EXPLODES,
            attacker_backfire=True,
            yield_multiplier=0,
        ),
    ),
    (range(5, 10), FalloutOutcome(SpinnerEffect.DUD, yield_multiplier=0)),
    (
        range(10, 23),
        FalloutOutcome(SpinnerEffect.SHELTER_SAVES, target_delta=-2),
    ),
    (
        range(23, 36),
        FalloutOutcome(SpinnerEffect.FIREBALL, target_delta=1),
    ),
    (range(36, 50), FalloutOutcome(SpinnerEffect.NO_RADIATION)),
    (
        range(50, 64),
        FalloutOutcome(SpinnerEffect.FALLOUT_2M, target_delta=2),
    ),
    (
        range(64, 77),
        FalloutOutcome(SpinnerEffect.FALLOUT_5M, target_delta=5),
    ),
    (
        range(77, 90),
        FalloutOutcome(SpinnerEffect.FALLOUT_10M, target_delta=10),
    ),
    (range(90, 95), FalloutOutcome(SpinnerEffect.DIRTY_BOMB, yield_multiplier=2)),
    (
        range(95, 100),
        FalloutOutcome(SpinnerEffect.STOCKPILE_EXPLODES, yield_multiplier=3),
    ),
]


def resolve_spinner(roll: int) -> FalloutOutcome:
    if not 0 <= roll <= 99:
        raise ValueError("Spinner roll must be between 0 and 99 inclusive")
    for roll_range, outcome in _SPINNER_TABLE:
        if roll in roll_range:
            return outcome
    raise RuntimeError("Spinner table incomplete")


def spin_spinner(rng: SeededRNG) -> tuple[int, FalloutOutcome]:
    roll = rng.randint(0, 99)
    return roll, resolve_spinner(roll)


def roll_nuke_die(rng: SeededRNG, postal_adjustment: bool = False) -> int:
    value = rng.randint(1, 6)
    if postal_adjustment:
        if value == 2:
            return 1
        if value == 6:
            return 5
    return value


# Source table id logged for postal equipment launch rolls, distinguishing the
# 6-sided Radioactive Fallout die from the base two-d10 fallout chart spinner
# (``ACTIVE_VARIANT.randomizer == "base_two_d10_fallout_chart"``).
RADIOACTIVE_FALLOUT_DIE_TABLE_ID = "postal_radioactive_fallout_die"


def roll_fallout_die(rng: SeededRNG) -> int:
    """Roll the postal Radioactive Fallout die.

    A plain uniform d6 with faces {cloud, 2, 3, 4, 5, 6}. Face 1 is the nuclear
    cloud (``is_fallout_cloud``): a launch failure or "explodes on launchpad"
    misfunction. Faces 2 through 6 are a successful launch. Distinct from the
    postal-adjusted ``roll_nuke_die`` (which collapses 2->1 and 6->5) and from
    the two-d10 ``spin_spinner`` fallout chart used for nuking.
    """
    return rng.randint(1, 6)


def is_fallout_cloud(roll: int) -> bool:
    """Return whether a Radioactive Fallout die roll is the nuclear cloud."""
    return roll == 1


__all__ = [
    "SpinnerEffect",
    "FalloutOutcome",
    "resolve_spinner",
    "spin_spinner",
    "roll_nuke_die",
    "RADIOACTIVE_FALLOUT_DIE_TABLE_ID",
    "roll_fallout_die",
    "is_fallout_cloud",
]
