"""Unit tests for the Radioactive Fallout die replay event builder."""

from __future__ import annotations

from nuclear_war_env.engine.spinner_events import fallout_die_result_event


def test_fallout_die_result_event_success_payload() -> None:
    event = fallout_die_result_event("player_0", "platform_1", 4)
    assert event.event_type == "fallout_die_result"
    assert event.player_id == "player_0"
    assert event.card_id == "platform_1"
    assert event.payload == {
        "raw_result": 4,
        "cloud": False,
        "randomizer": "postal_radioactive_fallout_die",
        "source_table_id": "postal_radioactive_fallout_die",
    }


def test_fallout_die_result_event_cloud_payload() -> None:
    event = fallout_die_result_event("player_1", None, 1)
    assert event.card_id is None
    assert event.payload["raw_result"] == 1
    assert event.payload["cloud"] is True
