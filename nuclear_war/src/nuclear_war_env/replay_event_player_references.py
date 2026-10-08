"""Replay event payload player-reference validators."""

from __future__ import annotations

from typing import Any

from .result_player_ids import validate_player_reference

TARGET_EVENT_TYPES = {
    "atomic_cannon_fired",
    "atomic_cannon_repositioned",
    "cruise_dropped",
    "cruise_launched",
    "final_strike_targeted",
    "launch_declared",
    "postal_atomic_cannon_reposition_ordered",
    "postal_atomic_cannon_setup_ordered",
    "postal_cruise_launch_ordered",
    "postal_cruise_move_ordered",
    "postal_propaganda_ordered",
    "postal_sabotage_ordered",
    "postal_secret_targeted",
    "postal_secret_theft_ordered",
    "postal_space_platform_drop_ordered",
    "postal_submarine_launch_ordered",
    "postal_submarine_reload_ordered",
    "postal_supervirus_pass_ordered",
    "postal_supervirus_start_ordered",
    "propaganda_effect",
    "secret_population_stolen",
    "secret_triggered",
    "secret_turns_lost",
    "space_platform_dropped",
    "space_shuttle_attacked",
    "submarine_strike",
    "supervirus_pass_failed",
    "supervirus_passed",
    "supervirus_started",
    "target_declared",
    "warhead_detonated",
}
TARGET_PLAYER_EVENT_TYPES = {
    "equipment_destroyed",
    "equipment_target_missed",
    "killer_satellite_destroyed_platform",
    "postal_killer_satellite_attack_ordered",
}


def validate_event_player_references(
    event: dict[str, Any], index: int, player_ids: set[str]
) -> None:
    event_type = str(event["event_type"])
    actor_id = event["player_id"]
    payload = event["payload"]
    if event_type in TARGET_EVENT_TYPES:
        _validate_field(
            event_type,
            payload,
            "target",
            index,
            player_ids,
            actor_id,
            reject_self=True,
        )
    if event_type in TARGET_PLAYER_EVENT_TYPES:
        _validate_field(
            event_type,
            payload,
            "target_player",
            index,
            player_ids,
            actor_id,
            reject_self=True,
        )
    if event_type == "cruise_move" and payload["target"] is not None:
        _validate_field(
            event_type,
            payload,
            "target",
            index,
            player_ids,
            actor_id,
            reject_self=True,
        )
    if event_type == "player_eliminated":
        _validate_field(
            event_type,
            payload,
            "by",
            index,
            player_ids,
            actor_id,
            reject_self=True,
            self_role="eliminated player",
        )
    if event_type == "sabotage_success":
        _validate_field(
            event_type,
            payload,
            "against",
            index,
            player_ids,
            actor_id,
            reject_self=True,
        )
    if event_type == "secret_stolen":
        _validate_field(
            event_type,
            payload,
            "from",
            index,
            player_ids,
            actor_id,
            reject_self=True,
        )


def _validate_field(
    event_type: str,
    payload: dict[str, Any],
    field: str,
    index: int,
    player_ids: set[str],
    actor_id: str,
    *,
    reject_self: bool = False,
    self_role: str = "acting player",
) -> None:
    validate_player_reference(
        payload[field],
        player_ids,
        f"Replay event {index} {event_type} {field}",
    )
    if reject_self and payload[field] == actor_id:
        raise ValueError(
            f"Replay event {index} {event_type} {field} must not be the {self_role}"
        )


__all__ = [
    "TARGET_EVENT_TYPES",
    "TARGET_PLAYER_EVENT_TYPES",
    "validate_event_player_references",
]
