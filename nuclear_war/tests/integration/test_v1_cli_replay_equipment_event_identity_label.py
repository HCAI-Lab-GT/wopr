"""CLI replay equipment event identity label tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


@pytest.mark.parametrize(
    ("event_type", "label"),
    [
        ("atomic_cannon_destroyed", "cannon"),
        ("atomic_cannon_discarded", "cannon"),
        ("atomic_cannon_failed", "cannon"),
        ("atomic_cannon_fired", "cannon"),
        ("atomic_cannon_repositioned", "cannon"),
        ("atomic_cannon_setup", "cannon"),
        ("postal_atomic_cannon_fire_ordered", "cannon"),
        ("postal_atomic_cannon_reposition_ordered", "cannon"),
        ("postal_atomic_cannon_setup_ordered", "cannon"),
        ("cruise_drop_failed", "missile"),
        ("cruise_drop_missed", "missile"),
        ("cruise_dropped", "missile"),
        ("cruise_launched", "missile"),
        ("cruise_move", "missile"),
        ("killer_satellite_destroyed_platform", "satellite"),
        ("postal_cruise_drop_ordered", "missile"),
        ("postal_cruise_launch_ordered", "missile"),
        ("postal_cruise_move_ordered", "missile"),
        ("killer_satellite_failed", "satellite"),
        ("killer_satellite_launched", "satellite"),
        ("postal_killer_satellite_attack_ordered", "satellite"),
        ("postal_killer_satellite_launch_ordered", "satellite"),
        ("space_platform_crashed", "platform"),
        ("space_platform_drop_missed", "platform"),
        ("space_platform_dropped", "platform"),
        ("space_platform_launch_failed", "platform"),
        ("space_platform_launched", "platform"),
        ("postal_space_platform_drop_ordered", "platform"),
        ("postal_space_platform_launch_ordered", "platform"),
        ("space_shuttle_attack_failed", "shuttle"),
        ("space_shuttle_attacked", "shuttle"),
        ("space_shuttle_reloaded", "shuttle"),
        ("postal_space_shuttle_attack_ordered", "shuttle"),
        ("postal_space_shuttle_reload_ordered", "shuttle"),
        ("submarine_destroyed", "submarine"),
        ("submarine_in_port", "submarine"),
        ("submarine_reloaded", "submarine"),
        ("submarine_returned", "submarine"),
        ("submarine_sent_to_sea", "submarine"),
        ("submarine_strike", "submarine"),
        ("postal_submarine_fire_ordered", "submarine"),
        ("postal_submarine_launch_ordered", "submarine"),
        ("postal_submarine_reload_ordered", "submarine"),
        ("postal_submarine_return_ordered", "submarine"),
    ],
)
def test_cli_replay_rejects_equipment_event_blank_card_id_with_label(
    tmp_path, capsys, event_type: str, label: str
) -> None:
    invalid = tmp_path / f"bad_{event_type}_blank_card_id.json"
    payload = _valid_postal_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": event_type,
        "player_id": "player_0",
        "card_id": "",
        "payload": {},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        f"Replay event 0 {event_type} card_id must identify a {label}" in captured.err
    )


def _valid_postal_replay_payload() -> dict:
    return {
        "mode": "postal",
        "active_variant": ACTIVE_VARIANT.to_payload(),
        "seed": 3,
        "agent": "heuristic",
        "players": 2,
        "winner": None,
        "turns": 1,
        "termination_reason": "max_turns",
        "eliminations": [],
        "final_populations": {"player_0": 30, "player_1": 30},
        "actions": [
            {
                "turn": 1,
                "player_id": "player_0",
                "action_id": "player_0:pass",
                "action_type": "pass",
                "payload": {},
            }
        ],
        "events": [
            {
                "turn": 1,
                "event_type": "action_passed",
                "player_id": "player_0",
                "card_id": None,
                "payload": {},
            }
        ],
    }
