"""C2 deliberation artifact identifier rejection tests."""

from __future__ import annotations

from typing import Any, cast

import pytest

from nuclear_war_concordia.c2_artifacts import validate_c2_artifact


def test_c2_artifact_rejects_duplicate_trace_reference(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    members = _members(artifact)
    members[1]["trace_ref"] = members[0]["trace_ref"]

    with pytest.raises(ValueError, match="duplicate trace_ref"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_duplicate_deliberation_id(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    deliberations = _deliberations(artifact)
    deliberations[1]["deliberation_id"] = deliberations[0]["deliberation_id"]

    with pytest.raises(ValueError, match="deliberation ids must be unique"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_malformed_deliberation_id(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    _deliberations(artifact)[0]["deliberation_id"] = None

    with pytest.raises(ValueError, match="non-empty strings"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_unscoped_trace_reference(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    _members(artifact)[0]["trace_ref"] = "arbitrary"

    with pytest.raises(ValueError, match="trace_ref scope"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_deliberation_id_outside_player_sequence(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    deliberation = _deliberations(artifact)[0]
    deliberation["deliberation_id"] = "arbitrary"
    for member in cast(list[dict[str, Any]], deliberation["members"]):
        member["trace_ref"] = f"arbitrary:{member['member_id']}"

    with pytest.raises(ValueError, match="does not match player sequence"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_member_trace_outside_deliberation_sequence(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    deliberation = _deliberations(artifact)[1]
    member = cast(list[dict[str, Any]], deliberation["members"])[0]
    trace = cast(dict[str, Any], member["trace"])
    trace["trace_id"] = f"{trace['player_id']}:{trace['turn']}:1"

    with pytest.raises(ValueError, match="trace_id does not match deliberation"):
        validate_c2_artifact(artifact, replay)


def _members(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], _deliberations(artifact)[0]["members"])


def _deliberations(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], artifact["deliberations"])
