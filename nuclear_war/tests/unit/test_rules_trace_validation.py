"""Rules trace validation payload tests."""

from __future__ import annotations

from nuclear_war_env.rules import validate_rules


def test_validate_rules_reports_rules_trace_payload() -> None:
    payload = validate_rules()

    assert payload["ok"] is True
    assert payload["rules_trace"]
    assert {
        item["record_type"]
        for item in payload["rules_trace"]
        if item["record_kind"] == "action"
    } >= {"advance", "draw", "enqueue", "target", "resolve"}


def test_validate_rules_reports_no_trace_source_gaps() -> None:
    payload = validate_rules()

    assert payload["rules_trace_source_gaps"] == []


def test_validate_rules_reports_rules_trace_step_payload() -> None:
    payload = validate_rules()

    assert payload["rules_trace_steps"]
    assert {item["step_id"] for item in payload["rules_trace_steps"]} >= {
        "draw_to_hand_target",
        "resolve_attack",
        "final_retaliation",
    }


def test_validate_rules_reports_no_trace_step_gaps() -> None:
    payload = validate_rules()

    assert payload["rules_trace_step_gaps"] == []


def test_validate_rules_reports_no_trace_step_source_gaps() -> None:
    payload = validate_rules()

    assert payload["rules_trace_step_source_gaps"] == []


def test_validate_rules_reports_full_game_rules_trace_summary() -> None:
    payload = validate_rules()

    assert payload["rules_trace_full_game"] == {
        "mode": "table",
        "players": 3,
        "seed": 1,
        "agent": "heuristic",
        # Re-pinned after the attack/retaliation fidelity fixes (wider
        # final-retaliation card pool -> seed-1 becomes a shorter mutual
        # annihilation) and the setup/peace fidelity fixes (the 6 SETUP_PLACE
        # opening-commitment actions, 3 players x 2 slots, add to the action and
        # trace counts but produce no events).
        "turns": 6,
        "termination_reason": "no_players_remaining",
        "action_count": 88,
        "event_count": 92,
        "trace_entry_count": 180,
        "gap_count": 0,
    }


def test_validate_rules_reports_no_full_game_rules_trace_gaps() -> None:
    payload = validate_rules()

    assert payload["rules_trace_full_game_gaps"] == []
