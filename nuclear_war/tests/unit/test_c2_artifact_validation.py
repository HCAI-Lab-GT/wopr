"""C2 deliberation artifact rejection tests."""

from __future__ import annotations

from typing import Any, cast

import pytest

from nuclear_war_concordia.c2_artifacts import validate_c2_artifact


def test_c2_artifact_rejects_non_integer_schema_version(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    artifact["schema_version"] = []

    with pytest.raises(ValueError, match="schema_version is invalid"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_missing_member(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    _members(artifact).pop()

    with pytest.raises(ValueError, match="exactly three members"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_illegal_member_vote(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    _members(artifact)[0]["vote_action_id"] = "not-a-legal-action"

    with pytest.raises(ValueError, match="vote action is not legal"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_malformed_member_vote(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    _members(artifact)[0]["vote_action_id"] = []

    with pytest.raises(ValueError, match="vote_action_id must be a string"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_member_option_set_mismatch(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    member = _members(artifact)[1]
    trace = cast(dict[str, Any], member["trace"])
    option = dict(cast(list[dict[str, Any]], trace["legal_options"])[0])
    option["action_id"] = "fabricated-advisory-option"
    cast(list[dict[str, Any]], trace["legal_options"]).append(option)
    observation = cast(dict[str, Any], trace["rendered_observation"])
    decision = cast(dict[str, Any], observation["decision"])
    decision["options"] = trace["legal_options"]
    member["vote_action_id"] = option["action_id"]
    trace["selected_action_id"] = option["action_id"]
    cast(dict[str, Any], trace["parse_result"])["action_id"] = option["action_id"]

    with pytest.raises(ValueError, match="member legal options do not match"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_truncated_authority_history(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    _deliberations(artifact).pop()

    with pytest.raises(ValueError, match="count does not match replay actions"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_fabricated_decision_type(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    deliberation = _deliberations(artifact)[0]
    deliberation["decision_type"] = "fabricated"
    for member in cast(list[dict[str, Any]], deliberation["members"]):
        cast(dict[str, Any], member["trace"])["decision_type"] = "fabricated"

    with pytest.raises(ValueError, match="decision_type"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_selected_action_not_linked_to_replay(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    _deliberations(artifact)[0]["selected_action_id"] = "missing-action"

    with pytest.raises(ValueError, match="does not link to replay action"):
        validate_c2_artifact(artifact, replay)


def test_c2_artifact_rejects_aggregation_mismatch(
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    _deliberations(artifact)[0]["rule"] = "forged-rule"

    with pytest.raises(ValueError, match="aggregation does not reproduce"):
        validate_c2_artifact(artifact, replay)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("fallback_used", True, "fallback"),
        ("validation_errors", ["No action_id parsed"], "malformed attempt"),
    ],
)
def test_c2_artifact_rejects_inadmissible_member_trace(
    field: str,
    value: object,
    message: str,
    c2_artifact_case: tuple[dict[str, Any], dict[str, Any]],
) -> None:
    replay, artifact = c2_artifact_case
    trace = cast(dict[str, Any], _members(artifact)[0]["trace"])
    trace[field] = value

    with pytest.raises(ValueError, match=message):
        validate_c2_artifact(artifact, replay)


def _members(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], _deliberations(artifact)[0]["members"])


def _deliberations(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    return cast(list[dict[str, Any]], artifact["deliberations"])
