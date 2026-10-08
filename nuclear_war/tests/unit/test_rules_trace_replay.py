"""Semantic rules trace replay tests."""

from __future__ import annotations

from nuclear_war_env.rules_trace_replay import (
    rules_trace_replay_gaps,
    rules_trace_replay_payload,
)


def test_rules_trace_replay_payload_maps_actions_and_events() -> None:
    replay = _replay_payload(
        actions=[
            {
                "turn": 1,
                "action_type": "draw",
            }
        ],
        events=[
            {
                "turn": 1,
                "event_type": "card_drawn",
            }
        ],
    )

    trace = rules_trace_replay_payload(replay)

    assert len(trace) == 2
    assert [entry["record_kind"] for entry in trace] == ["action", "event"]
    assert [entry["rule_step"] for entry in trace] == [
        "draw_to_hand_target",
        "draw_to_hand_target",
    ]


def test_rules_trace_replay_payload_has_required_fields() -> None:
    replay = _replay_payload(
        actions=[{"turn": 1, "action_type": "target"}],
        events=[{"turn": 1, "event_type": "target_declared"}],
    )

    trace = rules_trace_replay_payload(replay)

    for entry in trace:
        assert set(entry) == {
            "sequence",
            "turn",
            "record_kind",
            "record_type",
            "trace_id",
            "rule_step",
            "rule_area",
            "source_ids",
            "status",
        }
        assert entry["status"] == "semantic_mapped"
        assert isinstance(entry["source_ids"], list)
        assert entry["source_ids"]


def test_rules_trace_replay_gaps_reports_unmapped_action_family() -> None:
    replay = _replay_payload(
        actions=[{"turn": 1, "action_type": "unknown_action"}],
        events=[],
    )

    assert rules_trace_replay_gaps(replay) == [
        {
            "record_kind": "action",
            "record_type": "unknown_action",
            "turn": "1",
        }
    ]


def _replay_payload(
    actions: list[dict[str, object]],
    events: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "turns": 1,
        "actions": actions,
        "events": events,
    }
