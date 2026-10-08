"""LLM trace legal option validation tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.llm_trace_legal_options import validate_trace_legal_options


def test_trace_legal_options_rejects_missing_selected_action() -> None:
    trace = {
        "selected_action_id": "selected-action",
        "legal_options": [{"action_id": "different-action"}],
    }

    with pytest.raises(ValueError, match="selected_action_id missing"):
        validate_trace_legal_options(trace, 0)


def test_trace_legal_options_rejects_parsed_legal_action_mismatch() -> None:
    trace = {
        "selected_action_id": "selected-action",
        "legal_options": [
            {"action_id": "selected-action"},
            {"action_id": "other-legal-action"},
        ],
        "parse_result": {"action_id": "other-legal-action", "rationale": None},
    }

    with pytest.raises(ValueError, match="parse_result action_id"):
        validate_trace_legal_options(trace, 0)


def test_trace_legal_options_rejects_success_validation_error_count_mismatch() -> None:
    trace = {
        "selected_action_id": "selected-action",
        "legal_options": [{"action_id": "selected-action"}],
        "parse_result": {"action_id": "selected-action", "rationale": None},
        "retries": 1,
        "validation_errors": [],
    }

    with pytest.raises(ValueError, match="validation_errors"):
        validate_trace_legal_options(trace, 0)


def test_trace_legal_options_rejects_fallback_validation_error_count_mismatch() -> None:
    trace = {
        "selected_action_id": "selected-action",
        "legal_options": [{"action_id": "selected-action"}],
        "parse_result": {"action_id": None, "rationale": None},
        "retries": 1,
        "validation_errors": ["first failure"],
    }

    with pytest.raises(ValueError, match="validation_errors"):
        validate_trace_legal_options(trace, 0)


def test_trace_legal_options_rejects_forged_fallback_selection() -> None:
    # Fallback trace (parsed action was illegal), but selected is a legal option
    # that is neither options[0] ("first" policy) nor the pass option ("pass"
    # policy). A real agent could never produce this, so it is a forged/altered
    # trace and must be rejected.
    trace = {
        "selected_action_id": "p1:target",
        "legal_options": [
            {"action_id": "p1:launch", "action_type": "launch"},
            {"action_id": "p1:target", "action_type": "target"},
            {"action_id": "p1:pass", "action_type": "pass"},
        ],
        "parse_result": {"action_id": "p1:illegal", "rationale": None},
        "retries": 0,
        "validation_errors": ["Illegal action_id parsed: p1:illegal"],
    }

    with pytest.raises(ValueError, match="fallback target"):
        validate_trace_legal_options(trace, 0)


def test_trace_legal_options_accepts_pass_policy_fallback_selection() -> None:
    # A legitimate "pass" policy fallback selects the pass option, which is not
    # options[0]. The validator must accept it.
    trace = {
        "selected_action_id": "p1:pass",
        "legal_options": [
            {"action_id": "p1:launch", "action_type": "launch"},
            {"action_id": "p1:pass", "action_type": "pass"},
        ],
        "parse_result": {"action_id": "p1:illegal", "rationale": None},
        "retries": 0,
        "validation_errors": ["Illegal action_id parsed: p1:illegal"],
    }

    validate_trace_legal_options(trace, 0)


def test_trace_legal_options_accepts_first_policy_fallback_selection() -> None:
    # A legitimate "first" policy fallback selects options[0].
    trace = {
        "selected_action_id": "p1:launch",
        "legal_options": [
            {"action_id": "p1:launch", "action_type": "launch"},
            {"action_id": "p1:pass", "action_type": "pass"},
        ],
        "parse_result": {"action_id": "p1:illegal", "rationale": None},
        "retries": 0,
        "validation_errors": ["Illegal action_id parsed: p1:illegal"],
    }

    validate_trace_legal_options(trace, 0)
