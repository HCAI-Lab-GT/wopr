"""Press config parsing for Concordia harness runs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config_constants import PRESS_MODES

PRESS_FIELDS = {"mode", "enabled", "passes"}
_PASS_MODES = {"multi_turn_public", "full_press"}
_MISSING = object()


@dataclass(frozen=True)
class PressConfig:
    mode: str = "none"
    enabled: bool = False
    passes: int = 1


def load_press_config(payload: Any) -> PressConfig:
    if payload is None:
        return PressConfig()
    if not isinstance(payload, dict):
        raise ValueError("Concordia press config must be an object")
    if set(payload) - PRESS_FIELDS:
        raise ValueError("Concordia press config fields are invalid")
    mode = payload.get("mode", "none")
    enabled = payload.get("enabled", _MISSING)
    has_passes = "passes" in payload
    _validate_field_presence(mode, enabled, has_passes)
    if mode not in PRESS_MODES:
        allowed = sorted(PRESS_MODES)
        raise ValueError(f"Concordia press mode must be one of {allowed}")
    if not isinstance(enabled, bool):
        raise ValueError("Concordia press enabled must be a boolean")
    if mode == "none" and enabled:
        raise ValueError("Concordia press mode none cannot be enabled")
    passes = _load_passes(payload, mode)
    return PressConfig(mode=mode, enabled=enabled, passes=passes)


def _validate_field_presence(mode: Any, enabled: Any, has_passes: bool) -> None:
    if enabled is _MISSING:
        raise ValueError("Concordia press config requires both mode and enabled")
    if mode == "none" and not enabled:
        if has_passes:
            raise ValueError("Concordia press mode none must not set passes")
        return
    if mode in _PASS_MODES and not has_passes:
        raise ValueError(f"Concordia press mode {mode} requires passes")
    if mode not in _PASS_MODES and has_passes:
        raise ValueError(
            "Concordia press passes is only valid for multi_turn_public or full_press"
        )


def _load_passes(payload: dict[str, Any], mode: str) -> int:
    if mode not in _PASS_MODES:
        return 1
    passes = payload["passes"]
    if isinstance(passes, bool) or not isinstance(passes, int):
        raise ValueError("Concordia press passes must be an integer")
    if passes < 1:
        raise ValueError("Concordia press passes must be at least 1")
    return passes
