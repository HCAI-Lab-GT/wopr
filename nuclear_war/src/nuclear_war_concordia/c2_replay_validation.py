"""Replay alignment validation for C2 deliberation sidecars."""

from __future__ import annotations

from typing import Any

_AUTOMATIC_ACTION_TYPES = {"advance", "draw", "resolve"}


def validate_c2_replay_alignment(
    deliberations: list[dict[str, Any]],
    authority_players: Any,
    replay: dict[str, Any],
) -> None:
    players = _authority_players(authority_players, replay)
    if any(item["player_id"] not in players for item in deliberations):
        raise ValueError("C2 deliberation player is not an authority player")
    for player_id in players:
        player_deliberations = [
            item for item in deliberations if item["player_id"] == player_id
        ]
        player_actions = [
            action
            for action in replay["actions"]
            if action["player_id"] == player_id
            and action["action_type"] not in _AUTOMATIC_ACTION_TYPES
        ]
        if len(player_deliberations) != len(player_actions):
            raise ValueError(
                f"C2 authority player {player_id} deliberation count does not "
                "match replay actions"
            )
        for index, (deliberation, action) in enumerate(
            zip(player_deliberations, player_actions, strict=True)
        ):
            if (
                deliberation["selected_action_id"] != action["action_id"]
                or deliberation["turn"] != action["turn"]
            ):
                raise ValueError(
                    f"C2 authority player {player_id} deliberation {index} "
                    "does not link to replay action occurrence"
                )


def _authority_players(value: Any, replay: dict[str, Any]) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise ValueError("C2 artifact authority_players must be a list of strings")
    if value != sorted(set(value)):
        raise ValueError("C2 artifact authority_players must be sorted and unique")
    valid_players = {f"player_{index}" for index in range(replay["players"])}
    if any(item not in valid_players for item in value):
        raise ValueError("C2 artifact authority_players contains an unknown player")
    return value


__all__ = ["validate_c2_replay_alignment"]
