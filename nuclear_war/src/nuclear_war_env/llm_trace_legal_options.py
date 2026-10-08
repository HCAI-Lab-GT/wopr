"""Legal option validation for LLM trace artifacts."""

from __future__ import annotations

from typing import Any


def validate_trace_legal_options(trace: dict[str, Any], index: int) -> None:
    options = trace["legal_options"]
    selected = trace["selected_action_id"]
    legal_action_ids: set[str] = set()
    for option_index, option in enumerate(options):
        if not isinstance(option, dict):
            raise ValueError(f"Trace {index} legal_options entries must be objects")
        action_id = option.get("action_id")
        if not isinstance(action_id, str) or not action_id:
            raise ValueError(
                f"Trace {index} legal_options {option_index} action_id must be a string"
            )
        legal_action_ids.add(action_id)
    if selected not in legal_action_ids:
        raise ValueError(f"Trace {index} selected_action_id missing from legal_options")
    _validate_parse_result_selection(trace, legal_action_ids, selected, index)
    _validate_success_validation_error_count(trace, legal_action_ids, index)


def _validate_parse_result_selection(
    trace: dict[str, Any],
    legal_action_ids: set[str],
    selected: str,
    index: int,
) -> None:
    parse_result = trace.get("parse_result")
    if not isinstance(parse_result, dict):
        return
    parsed_action_id = parse_result.get("action_id")
    if parsed_action_id in legal_action_ids:
        if parsed_action_id != selected:
            raise ValueError(
                f"Trace {index} parse_result action_id "
                "does not match selected_action_id"
            )
        return
    # Fallback path: the parsed action was illegal/None, so the agent fell back to
    # a deterministic policy option. _fallback_option can only ever return
    # options[0] ("first") or the pass-type option ("pass", which itself degrades
    # to options[0] when no pass option is legal). The trace does not record which
    # policy fired, so we pin selected to that fixed target set; any other legal
    # option is a forged/altered fallback selection.
    targets = _fallback_targets(trace["legal_options"])
    if targets and selected not in targets:
        raise ValueError(
            f"Trace {index} selected_action_id is not a legal fallback target"
        )


def _fallback_targets(options: list[Any]) -> set[str]:
    if not options:
        return set()
    targets = {options[0].get("action_id")}
    for option in options:
        if option.get("action_type") == "pass":
            targets.add(option.get("action_id"))
            break
    return targets


def _validate_success_validation_error_count(
    trace: dict[str, Any],
    legal_action_ids: set[str],
    index: int,
) -> None:
    if "retries" not in trace or "validation_errors" not in trace:
        return
    parse_result = trace.get("parse_result")
    if not isinstance(parse_result, dict):
        return
    parsed_action_id = parse_result.get("action_id")
    expected_errors = (
        trace["retries"]
        if parsed_action_id in legal_action_ids
        else trace["retries"] + 1
    )
    if len(trace["validation_errors"]) != expected_errors:
        raise ValueError(f"Trace {index} validation_errors do not match retry outcome")


__all__ = ["validate_trace_legal_options"]
