"""Experiment replay result validation helpers."""

from __future__ import annotations

from typing import Any

from .experiment_result_values import validate_result_values
from .integer_validation import is_strict_int
from .replay_field_validation import validate_field_set
from .termination_reasons import validate_termination_reason
from .variants import validate_active_variant_payload

EXPERIMENT_RESULT_FIELDS = (
    "seed",
    "mode",
    "active_variant",
    "agent",
    "winner",
    "turns",
    "eliminations",
    "final_populations",
    "termination_reason",
)


def validate_experiment_results(results: Any, payload: dict[str, Any]) -> None:
    if not isinstance(results, list):
        raise ValueError("Experiment results must be a list")
    _validate_batch_numbers(payload)
    runs = payload["runs"]
    if len(results) != runs:
        raise ValueError(
            f"Experiment result count {len(results)} does not match runs: {runs}"
        )
    for index, result in enumerate(results):
        _validate_experiment_result(result, index, payload)


def _validate_batch_numbers(payload: dict[str, Any]) -> None:
    runs = payload["runs"]
    seed_start = payload["seed_start"]
    max_turns = payload["max_turns"]
    if not is_strict_int(runs) or runs < 1:
        raise ValueError(f"Experiment has invalid runs: {runs}")
    if not is_strict_int(seed_start):
        raise ValueError(f"Experiment has invalid seed_start: {seed_start}")
    if not is_strict_int(max_turns) or max_turns < 1:
        raise ValueError(f"Experiment has invalid max_turns: {max_turns}")


def _validate_experiment_result(
    result: Any, index: int, payload: dict[str, Any]
) -> None:
    if not isinstance(result, dict):
        raise ValueError(f"Experiment result {index} must be an object")
    for field in EXPERIMENT_RESULT_FIELDS:
        if field not in result:
            raise ValueError(
                f"Experiment result {index} missing required field: {field}"
            )
    validate_field_set(
        result,
        EXPERIMENT_RESULT_FIELDS,
        f"Experiment result {index}",
        ("pending_final_strikes",),
    )
    _validate_result_shapes(result, index)
    validate_result_values(result, index, payload["players"])
    _validate_result_context(result, index, payload)


def _validate_result_shapes(result: dict[str, Any], index: int) -> None:
    validate_active_variant_payload(
        result["active_variant"],
        f"Experiment result {index}",
    )
    if not isinstance(result["eliminations"], list):
        raise ValueError(f"Experiment result {index} eliminations must be a list")
    if not isinstance(result["final_populations"], dict):
        raise ValueError(
            f"Experiment result {index} final_populations must be an object"
        )
    validate_termination_reason(
        result["termination_reason"],
        f"Experiment result {index}",
    )


def _validate_result_context(
    result: dict[str, Any], index: int, payload: dict[str, Any]
) -> None:
    if not isinstance(result["mode"], str):
        raise ValueError(f"Experiment result {index} mode must be a string")
    if result["mode"] != payload["mode"]:
        raise ValueError(
            f"Experiment result {index} mode {result['mode']} "
            f"does not match batch mode: {payload['mode']}"
        )
    if not isinstance(result["agent"], str):
        raise ValueError(f"Experiment result {index} agent must be a string")
    if result["agent"] != payload["agent"]:
        raise ValueError(
            f"Experiment result {index} agent {result['agent']} "
            f"does not match batch agent: {payload['agent']}"
        )
    expected_seed = payload["seed_start"] + index
    if not is_strict_int(result["seed"]):
        raise ValueError(f"Experiment result {index} seed must be an integer")
    if result["seed"] != expected_seed:
        raise ValueError(
            f"Experiment result {index} seed {result['seed']} "
            f"does not match expected seed: {expected_seed}"
        )
    _validate_result_turns(result["turns"], index, payload["max_turns"])


def _validate_result_turns(turns: Any, index: int, max_turns: int) -> None:
    if not is_strict_int(turns) or turns < 1:
        raise ValueError(f"Experiment result {index} has invalid turns: {turns}")
    if turns > max_turns:
        raise ValueError(
            f"Experiment result {index} turns {turns} exceeds max_turns: {max_turns}"
        )


__all__ = ["validate_experiment_results"]
