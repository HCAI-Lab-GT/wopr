"""Concordia command-authority numeric edge tests."""

from __future__ import annotations

from typing import cast

import pytest

from nuclear_war_concordia.config import load_concordia_no_press_config


def test_sole_authority_deference_is_normalized_to_float(
    authority_config_payload: dict[str, object],
) -> None:
    authority = _authority(authority_config_payload)
    authority["parameters"] = {"deference": 1}

    config = load_concordia_no_press_config(authority_config_payload)

    parsed = config.seats["player_0"].authority
    assert parsed is not None
    assert parsed.parameters["deference"] == 1.0
    assert isinstance(parsed.parameters["deference"], float)


@pytest.mark.parametrize("deference", [float("nan"), float("inf"), float("-inf")])
def test_sole_authority_rejects_non_finite_deference(
    deference: float,
    authority_config_payload: dict[str, object],
) -> None:
    _authority(authority_config_payload)["parameters"] = {"deference": deference}

    with pytest.raises(ValueError, match="deference must be between 0 and 1"):
        load_concordia_no_press_config(authority_config_payload)


@pytest.mark.parametrize("threshold", [float("nan"), float("inf"), float("-inf")])
def test_council_rejects_non_finite_threshold(
    threshold: float,
    authority_config_payload: dict[str, object],
) -> None:
    authority = _authority(authority_config_payload)
    authority["archetype"] = "council"
    authority["parameters"] = _council_parameters(threshold=threshold)

    with pytest.raises(ValueError, match="threshold must be between 0 and 1"):
        load_concordia_no_press_config(authority_config_payload)


@pytest.mark.parametrize("weight", [float("nan"), float("inf"), float("-inf")])
def test_council_rejects_non_finite_weight(
    weight: float,
    authority_config_payload: dict[str, object],
) -> None:
    authority = _authority(authority_config_payload)
    authority["archetype"] = "council"
    weights: dict[str, object] = {member_id: 1 for member_id in _member_ids()}
    weights["executive"] = weight
    authority["parameters"] = _council_parameters(weights=weights)

    with pytest.raises(ValueError, match="weights must be positive numbers"):
        load_concordia_no_press_config(authority_config_payload)


def _authority(payload: dict[str, object]) -> dict[str, object]:
    seats = cast(dict[str, dict[str, object]], payload["seats"])
    return cast(dict[str, object], seats["player_0"]["authority"])


def _council_parameters(
    *, threshold: object = 0.5, weights: object | None = None
) -> dict[str, object]:
    return {
        "threshold": threshold,
        "weights": weights
        if weights is not None
        else {member_id: 1 for member_id in _member_ids()},
    }


def _member_ids() -> tuple[str, ...]:
    return "executive", "strategic_advisor", "risk_advisor"
