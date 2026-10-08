"""Per-variant acceptance criteria."""

from __future__ import annotations

from .variants import ACTIVE_VARIANT_ID

VARIANT_ACCEPTANCE_CRITERIA: dict[str, tuple[str, ...]] = {
    ACTIVE_VARIANT_ID: (
        "10-card hand draw target verified",
        "40-card population deck verified",
        "two-d10 fallout chart verified",
        "initial face-down setup verified",
        "no press or expansion behavior enabled",
    ),
    "classic_spinner_scan": (
        "spinner probabilities transcribed",
        "9-card hand model verified",
        "classic deck boundary verified",
    ),
    "nuclear_destruction_modern": (
        "ND deck composition verified",
        "Nuclear Escalation die rules verified",
        "six-player mat rules verified",
    ),
    "postal_press": (
        "press adjudication rules verified",
        "simultaneous order timing verified",
        "communication boundary verified",
    ),
    "no_press_house": (
        "house-mode boundary documented",
        "press-disabled behavior verified",
        "variant source status documented",
    ),
    "combined_expansions": (
        "authorized expansion deck composition verified",
        "per-mechanic mode availability verified",
        "exact card effect source verified",
    ),
}

__all__ = ["VARIANT_ACCEPTANCE_CRITERIA"]
