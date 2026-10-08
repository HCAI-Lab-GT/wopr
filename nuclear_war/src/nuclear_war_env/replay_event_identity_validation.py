"""Replay event identity validation helpers."""

from __future__ import annotations

from typing import Any

from .replay_event_identity_labels import event_card_id_label

CARD_ID_REQUIRED_EVENT_TYPES = {
    "atomic_cannon_destroyed",
    "atomic_cannon_discarded",
    "atomic_cannon_failed",
    "atomic_cannon_fired",
    "atomic_cannon_repositioned",
    "atomic_cannon_setup",
    "card_drawn",
    "card_resolved",
    "cruise_drop_failed",
    "cruise_drop_missed",
    "cruise_dropped",
    "cruise_launched",
    "cruise_move",
    "defense_prepared",
    "delivery_ready",
    "equipment_destroyed",
    "equipment_target_failed",
    "equipment_target_missed",
    "intercept_success",
    "killer_satellite_destroyed_platform",
    "killer_satellite_failed",
    "killer_satellite_launched",
    "launch_declared",
    "postal_atomic_cannon_fire_ordered",
    "postal_atomic_cannon_reposition_ordered",
    "postal_atomic_cannon_setup_ordered",
    "postal_cruise_drop_ordered",
    "postal_cruise_launch_ordered",
    "postal_cruise_move_ordered",
    "postal_defense_ordered",
    "postal_killer_satellite_attack_ordered",
    "postal_killer_satellite_launch_ordered",
    "postal_propaganda_ordered",
    "postal_secret_targeted",
    "postal_space_platform_drop_ordered",
    "postal_space_platform_launch_ordered",
    "postal_space_shuttle_attack_ordered",
    "postal_space_shuttle_reload_ordered",
    "postal_submarine_fire_ordered",
    "postal_submarine_launch_ordered",
    "postal_submarine_reload_ordered",
    "postal_submarine_return_ordered",
    "postal_supervirus_start_ordered",
    "propaganda_effect",
    "propaganda_ready",
    "secret_queued",
    "secret_population_damaged",
    "secret_population_gained",
    "secret_population_removed",
    "secret_population_stolen",
    "secret_stolen",
    "secret_triggered",
    "secret_turns_lost",
    "space_platform_crashed",
    "space_platform_drop_missed",
    "space_platform_dropped",
    "space_platform_launch_failed",
    "space_platform_launched",
    "space_shuttle_attack_failed",
    "space_shuttle_attacked",
    "space_shuttle_reloaded",
    "special_played",
    "submarine_destroyed",
    "submarine_in_port",
    "submarine_reloaded",
    "submarine_returned",
    "submarine_sent_to_sea",
    "submarine_strike",
    "supervirus_cured",
    "supervirus_immunity",
    "supervirus_pass_failed",
    "supervirus_passed",
    "supervirus_retained",
    "supervirus_started",
    "supervirus_wiped_out",
    "target_declared",
    "warhead_discarded",
    "warhead_loaded",
}
PLAYER_ID_REQUIRED_EVENT_TYPES = CARD_ID_REQUIRED_EVENT_TYPES | {
    "action_passed",
    "cards_enqueued",
    "cruise_launch_failed",
    "fallout_die_result",
    "final_strike_executed",
    "final_strike_targeted",
    "launch_backfire",
    "postal_peace_voted",
    "postal_secret_theft_ordered",
    "postal_supervirus_pass_ordered",
    "queue_updated",
    "spinner_result",
    "turn_skipped",
    "warhead_detonated",
}


def validate_event_identity(event: dict[str, Any], index: int) -> None:
    event_type = event["event_type"]
    if event_type in PLAYER_ID_REQUIRED_EVENT_TYPES and event["player_id"] is None:
        raise ValueError(
            f"Replay event {index} {event_type} player_id must identify a player"
        )
    if event_type in CARD_ID_REQUIRED_EVENT_TYPES and not event["card_id"]:
        label = event_card_id_label(event_type)
        raise ValueError(
            f"Replay event {index} {event_type} card_id must identify a {label}"
        )
    if event_type == "player_eliminated" and event["player_id"] is None:
        raise ValueError(
            f"Replay event {index} player_eliminated player_id "
            "must be the eliminated player"
        )


__all__ = [
    "CARD_ID_REQUIRED_EVENT_TYPES",
    "PLAYER_ID_REQUIRED_EVENT_TYPES",
    "validate_event_identity",
]
