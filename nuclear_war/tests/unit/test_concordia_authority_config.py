"""Concordia command-authority config tests."""

from __future__ import annotations

from typing import cast

import pytest

from nuclear_war_concordia.config import load_concordia_no_press_config


def test_load_concordia_config_accepts_three_member_authority(
    authority_config_payload: dict[str, object],
) -> None:
    config = load_concordia_no_press_config(authority_config_payload)

    authority = config.seats["player_0"].authority
    assert authority is not None
    assert authority.archetype == "sole_authority"
    assert authority.spokesperson == "executive"
    assert [member.member_id for member in authority.members] == [
        "executive",
        "strategic_advisor",
        "risk_advisor",
    ]


def test_load_concordia_config_requires_three_authority_members(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    _members(payload).pop()

    with pytest.raises(ValueError, match="exactly three members"):
        load_concordia_no_press_config(payload)


def test_load_concordia_config_rejects_duplicate_authority_member_ids(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    _members(payload)[2]["member_id"] = "strategic_advisor"

    with pytest.raises(ValueError, match="member ids must be unique"):
        load_concordia_no_press_config(payload)


def test_load_concordia_config_requires_spokesperson_member(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    _authority(payload)["spokesperson"] = "outsider"

    with pytest.raises(ValueError, match="spokesperson must name a member"):
        load_concordia_no_press_config(payload)


def test_load_concordia_config_rejects_unknown_authority_archetype(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    _authority(payload)["archetype"] = "distributed"

    with pytest.raises(ValueError, match="archetype must be one of"):
        load_concordia_no_press_config(payload)


def test_load_concordia_config_requires_sole_authority_executive(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    _members(payload)[0]["member_id"] = "chair"
    _authority(payload)["spokesperson"] = "chair"

    with pytest.raises(ValueError, match="requires an executive member"):
        load_concordia_no_press_config(payload)


def test_load_concordia_config_rejects_authority_on_scripted_seat(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    _seat(payload)["agent"] = "concordia_scripted"
    _seat(payload)["scripted_responses"] = ['{"action_id": "unused"}']

    with pytest.raises(ValueError, match="authority requires"):
        load_concordia_no_press_config(payload)


def test_load_concordia_config_rejects_duplicate_member_names(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    second_identity = cast(dict[str, str], _members(payload)[1]["identity"])
    second_identity["name"] = "Executive"

    with pytest.raises(ValueError, match="member names must be unique"):
        load_concordia_no_press_config(payload)


def test_load_concordia_config_accepts_authority_on_http_seat(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    _seat(payload)["agent"] = "concordia_http"
    _seat(payload)["client"] = {
        "base_url": "http://localhost:8000/v1",
        "model": "test-model",
    }

    config = load_concordia_no_press_config(payload)

    assert config.seats["player_0"].authority is not None


@pytest.mark.parametrize("field", ["member_id", "name"])
def test_load_concordia_config_rejects_empty_member_names(
    field: str,
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    member = _members(payload)[1]
    if field == "member_id":
        member[field] = ""
    else:
        identity = cast(dict[str, str], member["identity"])
        identity[field] = ""

    with pytest.raises(ValueError, match="must not be empty"):
        load_concordia_no_press_config(payload)


def _seat(payload: dict[str, object]) -> dict[str, object]:
    seats = cast(dict[str, dict[str, object]], payload["seats"])
    return seats["player_0"]


def _authority(payload: dict[str, object]) -> dict[str, object]:
    return cast(dict[str, object], _seat(payload)["authority"])


def _members(payload: dict[str, object]) -> list[dict[str, object]]:
    return cast(list[dict[str, object]], _authority(payload)["members"])
