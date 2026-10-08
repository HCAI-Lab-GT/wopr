"""Concordia command-authority parameter validation tests."""

from __future__ import annotations

from typing import cast

import pytest

from nuclear_war_concordia.config import load_concordia_no_press_config


def test_authority_config_requires_parameters(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    authority = _authority(payload)
    del authority["parameters"]

    with pytest.raises(ValueError, match="requires parameters"):
        load_concordia_no_press_config(payload)


@pytest.mark.parametrize("deference", [True, "zero", -0.1, 1.1])
def test_sole_authority_requires_bounded_numeric_deference(
    deference: object,
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    _authority(payload)["parameters"] = {"deference": deference}

    with pytest.raises(ValueError, match="deference must be between 0 and 1"):
        load_concordia_no_press_config(payload)


@pytest.mark.parametrize(
    "parameters",
    [{}, {"deference": 0.0, "unexpected": True}],
)
def test_sole_authority_requires_exact_parameter_fields(
    parameters: dict[str, object],
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    _authority(payload)["parameters"] = parameters

    with pytest.raises(ValueError, match="parameter fields must be"):
        load_concordia_no_press_config(payload)


def test_council_parameters_are_normalized(
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    authority = _authority(payload)
    authority["archetype"] = "council"
    authority["parameters"] = {
        "threshold": 2 / 3,
        "weights": {
            "executive": 1,
            "strategic_advisor": 1,
            "risk_advisor": 1,
        },
    }

    config = load_concordia_no_press_config(payload)

    parsed = config.seats["player_0"].authority
    assert parsed is not None
    weights = cast(dict[str, float], parsed.parameters["weights"])
    assert all(isinstance(weight, float) for weight in weights.values())
    assert parsed.parameters["threshold"] == pytest.approx(2 / 3)


@pytest.mark.parametrize("parameters", [{}, {"weights": {}, "threshold": 0.5, "x": 1}])
def test_council_requires_exact_parameter_fields(
    parameters: dict[str, object],
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    authority = _authority(payload)
    authority["archetype"] = "council"
    authority["parameters"] = parameters

    with pytest.raises(ValueError, match="parameter fields must be"):
        load_concordia_no_press_config(payload)


@pytest.mark.parametrize("threshold", [True, "high", 0.0, 1.1])
def test_council_requires_bounded_numeric_threshold(
    threshold: object,
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    authority = _authority(payload)
    authority["archetype"] = "council"
    authority["parameters"] = _council_parameters(threshold=threshold)

    with pytest.raises(ValueError, match="threshold must be between 0 and 1"):
        load_concordia_no_press_config(payload)


@pytest.mark.parametrize(
    "weights",
    [
        {},
        {"executive": 1, "strategic_advisor": 1, "outsider": 1},
        {"executive": 0, "strategic_advisor": 1, "risk_advisor": 1},
        {"executive": True, "strategic_advisor": 1, "risk_advisor": 1},
    ],
)
def test_council_requires_positive_member_weights(
    weights: object,
    authority_config_payload: dict[str, object],
) -> None:
    payload = authority_config_payload
    authority = _authority(payload)
    authority["archetype"] = "council"
    authority["parameters"] = _council_parameters(weights=weights)

    with pytest.raises(ValueError, match="weights"):
        load_concordia_no_press_config(payload)


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
