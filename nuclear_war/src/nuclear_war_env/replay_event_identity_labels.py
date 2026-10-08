"""Replay event identity label helpers."""

from __future__ import annotations

EVENT_CARD_ID_LABELS = {
    "atomic_cannon_destroyed": "cannon",
    "atomic_cannon_discarded": "cannon",
    "atomic_cannon_failed": "cannon",
    "atomic_cannon_fired": "cannon",
    "atomic_cannon_repositioned": "cannon",
    "atomic_cannon_setup": "cannon",
    "postal_atomic_cannon_fire_ordered": "cannon",
    "postal_atomic_cannon_reposition_ordered": "cannon",
    "postal_atomic_cannon_setup_ordered": "cannon",
    "cruise_drop_failed": "missile",
    "cruise_drop_missed": "missile",
    "cruise_dropped": "missile",
    "cruise_launched": "missile",
    "cruise_move": "missile",
    "postal_cruise_drop_ordered": "missile",
    "postal_cruise_launch_ordered": "missile",
    "postal_cruise_move_ordered": "missile",
    "killer_satellite_destroyed_platform": "satellite",
    "killer_satellite_failed": "satellite",
    "killer_satellite_launched": "satellite",
    "postal_killer_satellite_attack_ordered": "satellite",
    "postal_killer_satellite_launch_ordered": "satellite",
    "space_platform_crashed": "platform",
    "space_platform_drop_missed": "platform",
    "space_platform_dropped": "platform",
    "space_platform_launch_failed": "platform",
    "space_platform_launched": "platform",
    "postal_space_platform_drop_ordered": "platform",
    "postal_space_platform_launch_ordered": "platform",
    "space_shuttle_attack_failed": "shuttle",
    "space_shuttle_attacked": "shuttle",
    "space_shuttle_reloaded": "shuttle",
    "postal_space_shuttle_attack_ordered": "shuttle",
    "postal_space_shuttle_reload_ordered": "shuttle",
    "submarine_destroyed": "submarine",
    "submarine_in_port": "submarine",
    "submarine_reloaded": "submarine",
    "postal_submarine_fire_ordered": "submarine",
    "postal_submarine_launch_ordered": "submarine",
    "postal_submarine_reload_ordered": "submarine",
    "postal_submarine_return_ordered": "submarine",
    "submarine_returned": "submarine",
    "submarine_sent_to_sea": "submarine",
    "submarine_strike": "submarine",
}


def event_card_id_label(event_type: str) -> str:
    return EVENT_CARD_ID_LABELS.get(event_type, "card")


__all__ = ["EVENT_CARD_ID_LABELS", "event_card_id_label"]
