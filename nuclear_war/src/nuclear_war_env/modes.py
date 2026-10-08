"""Runtime mode validation."""

from __future__ import annotations

from .state import Ruleset

VALID_MODES = {"table", "postal"}


def ruleset_for_mode(mode: str) -> Ruleset:
    if mode == "table":
        return Ruleset.TABLE
    if mode == "postal":
        return Ruleset.POSTAL
    raise ValueError(f"Unknown mode: {mode}")


__all__ = ["VALID_MODES", "ruleset_for_mode"]
