"""C2 deliberation artifact construction tests."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

import pytest

from nuclear_war_concordia.c2_artifacts import (
    C2_SCHEMA_VERSION,
    build_c2_artifact,
    validate_c2_artifact,
)
from nuclear_war_concordia.harness_seat_runtime import ConcordiaSeatRuntime
from nuclear_war_env.simulation import SimulationConfig, run_simulation


def test_c2_artifact_accepts_empty_runtime_mapping() -> None:
    replay = run_simulation(
        SimulationConfig(
            mode="table",
            players=3,
            seed=11,
            agent="decision_heuristic",
            max_turns=1,
        )
    )

    artifact = build_c2_artifact(replay, {})

    assert artifact["schema_version"] == C2_SCHEMA_VERSION
    assert artifact["deliberations"] == []
    validate_c2_artifact(artifact, replay)


def test_c2_schema_v1_rejects_nested_trace_fields_beyond_v5(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    deliberations = cast(list[dict[str, Any]], artifact["deliberations"])
    members = cast(list[dict[str, Any]], deliberations[0]["members"])
    trace = cast(dict[str, Any], members[0]["trace"])
    trace["future_schema_field"] = None

    with pytest.raises(ValueError, match="fields are invalid"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_builds_member_records_from_authority_runtime(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case

    assert artifact["deliberations"]
    first = artifact["deliberations"][0]
    assert first["player_id"] == "player_0"
    assert first["selected_action_id"] in {
        action["action_id"] for action in replay["actions"]
    }
    assert [record["member_id"] for record in first["members"]] == [
        "executive",
        "strategic_advisor",
        "risk_advisor",
    ]
    assert all(record["trace"] for record in first["members"])


def test_c2_artifact_rejects_missing_authority_trace_sinks(
    c2_runtime_case: tuple[dict[str, Any], dict[str, ConcordiaSeatRuntime]],
) -> None:
    replay, runtimes = c2_runtime_case
    runtimes["player_0"].member_traces.clear()

    with pytest.raises(ValueError, match="exactly three member trace sinks"):
        build_c2_artifact(replay, runtimes)


def test_c2_artifact_replays_council_aggregation(
    authority_config_payload: dict[str, object],
    c2_artifact_factory: Callable[
        [dict[str, object]], tuple[dict[str, Any], dict[str, Any]]
    ],
) -> None:
    seats = cast(dict[str, dict[str, Any]], authority_config_payload["seats"])
    authority = cast(dict[str, Any], seats["player_0"]["authority"])
    authority["archetype"] = "council"
    authority["parameters"] = {
        "threshold": 0.5,
        "weights": {
            "executive": 1.0,
            "strategic_advisor": 1.0,
            "risk_advisor": 1.0,
        },
    }

    replay, artifact = c2_artifact_factory(authority_config_payload)

    assert artifact["deliberations"]
    assert artifact["deliberations"][0]["archetype"] == "council"
    validate_c2_artifact(artifact, replay)
