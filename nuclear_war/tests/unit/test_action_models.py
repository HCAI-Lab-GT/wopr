"""Action model tests."""

from __future__ import annotations

import math

import pytest

from nuclear_war_env.action_models import ActionType, build_action


def test_build_action_payload_suffix_is_key_order_independent() -> None:
    first = build_action(
        "p1",
        ActionType.TARGET,
        "Target p2",
        {"delivery": "delivery", "target": "p2"},
    )
    second = build_action(
        "p1",
        ActionType.TARGET,
        "Target p2",
        {"target": "p2", "delivery": "delivery"},
    )

    assert first.action_id == second.action_id


def test_build_action_payload_suffix_distinguishes_delimiter_values() -> None:
    one_field = build_action(
        "p1",
        ActionType.TARGET,
        "Target p2",
        {"a": "1:b=2"},
    )
    two_fields = build_action(
        "p1",
        ActionType.TARGET,
        "Target p2",
        {"a": "1", "b": "2"},
    )

    assert one_field.action_id != two_fields.action_id


def test_build_action_copies_payload_input() -> None:
    payload = {"delivery": "delivery", "target": "p2"}
    action = build_action("p1", ActionType.TARGET, "Target p2", payload)

    payload["target"] = "p3"

    assert action.payload == {"delivery": "delivery", "target": "p2"}


def test_build_action_rejects_non_finite_payload_values() -> None:
    with pytest.raises(
        ValueError,
        match="Out of range float values are not JSON compliant",
    ):
        build_action("p1", ActionType.PASS, "Pass", {"value": math.nan})
