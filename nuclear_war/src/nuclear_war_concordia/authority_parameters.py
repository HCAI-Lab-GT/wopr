"""Validation and normalization for command-authority parameters."""

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
from typing import TypeGuard

Numeric = int | float


def normalized_authority_parameters(
    archetype: str,
    parameters: Mapping[object, object],
    member_ids: list[str],
    context: str,
) -> dict[str, object]:
    if archetype == "sole_authority":
        return _sole_authority_parameters(parameters, context)
    return _council_parameters(parameters, member_ids, context)


def _sole_authority_parameters(
    parameters: Mapping[object, object], context: str
) -> dict[str, object]:
    if set(parameters) != {"deference"}:
        raise ValueError(f"{context} authority parameter fields must be ['deference']")
    deference = parameters["deference"]
    if not _bounded_number(deference):
        raise ValueError(f"{context} authority deference must be between 0 and 1")
    return {"deference": float(deference)}


def _council_parameters(
    parameters: Mapping[object, object], member_ids: list[str], context: str
) -> dict[str, object]:
    if set(parameters) != {"threshold", "weights"}:
        raise ValueError(
            f"{context} authority parameter fields must be ['threshold', 'weights']"
        )
    threshold = parameters["threshold"]
    if not _positive_bounded_number(threshold):
        raise ValueError(f"{context} authority threshold must be between 0 and 1")
    weights = parameters["weights"]
    if not isinstance(weights, dict) or set(weights) != set(member_ids):
        raise ValueError(f"{context} authority weights must name exactly the members")
    normalized_weights: dict[str, float] = {}
    for member_id in member_ids:
        weight = weights[member_id]
        if not _positive_number(weight):
            raise ValueError(f"{context} authority weights must be positive numbers")
        normalized_weights[member_id] = float(weight)
    return {
        "threshold": float(threshold),
        "weights": normalized_weights,
    }


def _bounded_number(value: object) -> TypeGuard[Numeric]:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and isfinite(float(value))
        and 0.0 <= float(value) <= 1.0
    )


def _positive_bounded_number(value: object) -> TypeGuard[Numeric]:
    if not _bounded_number(value):
        return False
    return float(value) > 0.0


def _positive_number(value: object) -> TypeGuard[Numeric]:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and isfinite(float(value))
        and float(value) > 0.0
    )


__all__ = ["normalized_authority_parameters"]
