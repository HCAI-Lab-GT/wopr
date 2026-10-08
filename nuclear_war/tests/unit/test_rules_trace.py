"""Rules trace catalog tests."""

from __future__ import annotations

from nuclear_war_env.rules_trace import (
    rules_trace_payload,
    rules_trace_source_gaps,
    rules_trace_step_gaps,
    rules_trace_step_payload,
    rules_trace_step_source_gaps,
)

REQUIRED_ACTION_TYPES = {
    "advance",
    "draw",
    "enqueue",
    "modify_deterrent",
    "target",
    "intercept",
    "secret_target",
    "propaganda_target",
    "final_strike_target",
    "resolve",
}

REQUIRED_EVENT_TYPES = {
    "card_drawn",
    "cards_enqueued",
    "delivery_ready",
    "warhead_loaded",
    "target_declared",
    "launch_declared",
    "intercept_success",
    "spinner_result",
    "warhead_detonated",
    "propaganda_effect",
    "secret_triggered",
}

REQUIRED_RULE_STEPS = {
    "slide_launch_track",
    "draw_to_hand_target",
    "place_face_down_card",
    "modify_deterrents",
    "declare_attack_target",
    "defender_intercept_response",
    "resolve_secret_or_top_secret",
    "resolve_peace_propaganda",
    "final_retaliation_targeting",
    "resolve_attack",
    "resolve_face_up_card",
    "load_delivery_system",
    "discard_attack_cards",
    "apply_fallout_randomizer",
    "apply_population_loss",
    "apply_elimination",
    "restore_peace_after_elimination",
    "secret_effect",
    "final_retaliation",
}


def test_rules_trace_payload_reports_required_table_action_mappings() -> None:
    payload = rules_trace_payload()

    mapped = {
        item["record_type"] for item in payload if item["record_kind"] == "action"
    }

    assert mapped >= REQUIRED_ACTION_TYPES


def test_rules_trace_payload_reports_required_table_event_mappings() -> None:
    payload = rules_trace_payload()

    mapped = {item["record_type"] for item in payload if item["record_kind"] == "event"}

    assert mapped >= REQUIRED_EVENT_TYPES


def test_rules_trace_payload_has_required_fields() -> None:
    payload = rules_trace_payload()

    for item in payload:
        assert set(item) == {
            "trace_id",
            "record_kind",
            "record_type",
            "rule_step",
            "source_ids",
            "status",
        }
        assert item["record_kind"] in {"action", "event"}
        assert item["status"] == "scaffolded"
        assert isinstance(item["source_ids"], list)
        assert item["source_ids"]


def test_rules_trace_source_gaps_reports_unknown_source_ids() -> None:
    gaps = rules_trace_source_gaps({"MIR-001"})

    assert {"trace_id": "table.turn.advance", "source_id": "MIR-002"} in gaps


def test_rules_trace_step_payload_reports_required_rule_steps() -> None:
    payload = rules_trace_step_payload()

    mapped = {item["step_id"] for item in payload}

    assert mapped >= REQUIRED_RULE_STEPS


def test_rules_trace_step_payload_has_required_fields() -> None:
    payload = rules_trace_step_payload()

    for item in payload:
        assert set(item) == {
            "step_id",
            "rule_area",
            "summary",
            "source_ids",
            "status",
        }
        assert item["status"] == "source_mapped"
        assert isinstance(item["source_ids"], list)
        assert item["source_ids"]


def test_rules_trace_step_gaps_reports_no_unknown_steps() -> None:
    assert rules_trace_step_gaps() == []


def test_rules_trace_step_source_gaps_reports_unknown_source_ids() -> None:
    gaps = rules_trace_step_source_gaps({"MIR-001"})

    assert {"step_id": "slide_launch_track", "source_id": "MIR-002"} in gaps
