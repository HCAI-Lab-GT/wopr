"""Spinner and Radioactive Fallout die event construction helpers."""

from __future__ import annotations

from nuclear_war_env.fallout import (
    RADIOACTIVE_FALLOUT_DIE_TABLE_ID,
    FalloutOutcome,
    is_fallout_cloud,
)
from nuclear_war_env.variants import ACTIVE_VARIANT

from .events import EngineEvent


def spinner_result_event(
    player_id: str,
    card_id: str | None,
    roll: int,
    outcome: FalloutOutcome,
) -> EngineEvent:
    return EngineEvent(
        "spinner_result",
        player_id,
        card_id,
        {
            "raw_result": roll,
            "effect": outcome.effect.value,
            "multiplier": outcome.yield_multiplier,
            "target_adjustment": outcome.target_delta,
            "randomizer": ACTIVE_VARIANT.randomizer,
            "source_table_id": ACTIVE_VARIANT.randomizer,
        },
    )


def fallout_die_result_event(
    player_id: str,
    card_id: str | None,
    roll: int,
) -> EngineEvent:
    """Build the replay event for a postal Radioactive Fallout die roll.

    Logged for postal equipment launch/attack rolls that use the 6-sided die
    (cloud=1 failure, 2-6 success) instead of the two-d10 fallout chart spinner.
    The ``randomizer``/``source_table_id`` distinguish it from ``spinner_result``.
    """
    return EngineEvent(
        "fallout_die_result",
        player_id,
        card_id,
        {
            "raw_result": roll,
            "cloud": is_fallout_cloud(roll),
            "randomizer": RADIOACTIVE_FALLOUT_DIE_TABLE_ID,
            "source_table_id": RADIOACTIVE_FALLOUT_DIE_TABLE_ID,
        },
    )


__all__ = ["spinner_result_event", "fallout_die_result_event"]
