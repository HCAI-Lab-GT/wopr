"""Identifier validation for C2 deliberation sidecars."""

from __future__ import annotations

from typing import Any


def validate_c2_deliberation_identity(
    deliberation: dict[str, Any],
    seen_ids: set[str],
    next_indices: dict[str, int],
) -> None:
    deliberation_id = deliberation["deliberation_id"]
    if not isinstance(deliberation_id, str) or not deliberation_id:
        raise ValueError("C2 deliberation ids must be unique non-empty strings")
    if deliberation_id in seen_ids:
        raise ValueError("C2 deliberation ids must be unique non-empty strings")
    player_id = deliberation["player_id"]
    if not isinstance(player_id, str) or not player_id:
        raise ValueError("C2 deliberation player_id must be a non-empty string")
    expected_index = next_indices.get(player_id, 1)
    if deliberation_id != f"c2:{player_id}:{expected_index}":
        raise ValueError("C2 deliberation id does not match player sequence")
    seen_ids.add(deliberation_id)
    next_indices[player_id] = expected_index + 1


__all__ = ["validate_c2_deliberation_identity"]
