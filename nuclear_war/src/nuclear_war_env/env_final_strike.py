"""Final-strike lifecycle helpers for environments.

The predicate itself is owned by the engine (``engine.terminal``); this module
keeps the historical environment-facing name.
"""

from __future__ import annotations

from .engine.terminal import player_final_strike_pending as has_final_strike_activity

__all__ = ["has_final_strike_activity"]
