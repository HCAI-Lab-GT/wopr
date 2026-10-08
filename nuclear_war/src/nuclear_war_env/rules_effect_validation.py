"""Effect metadata helpers for rule validation."""

from __future__ import annotations

from typing import Any

from .engine.postal.secret_effects import SUPPORTED_EFFECT_KEYS


def unsupported_effect_keys(registry: dict[str, Any]) -> list[str]:
    keys: set[str] = set()
    for record in registry.values():
        effect = record.data.get("effect", {})
        if isinstance(effect, dict):
            keys.update(str(key) for key in effect)
    return sorted(keys - SUPPORTED_EFFECT_KEYS)


def postal_special_effects(registry: dict[str, Any]) -> list[str]:
    return sorted(
        str(record.data["postal_effect"])
        for record in registry.values()
        if record.data.get("postal_effect")
    )


__all__ = ["postal_special_effects", "unsupported_effect_keys"]
