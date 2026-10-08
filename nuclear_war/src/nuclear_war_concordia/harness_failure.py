"""Run-level Concordia failure construction."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .c2_partial import build_c2_partial_state
from .config import ConcordiaNoPressConfig
from .failure import (
    ConcordiaDecisionFailure,
    ConcordiaRunFailure,
    run_failure_snapshot,
)
from .harness_payloads import agent_metadata, config_snapshot, runtime_payload
from .harness_seat_runtime import ConcordiaSeatRuntime
from .types import ConcordiaRuntimeStatus


def budget_failure(error: BaseException) -> ConcordiaDecisionFailure:
    return ConcordiaDecisionFailure(
        str(error),
        {
            "decision_type": "budget",
            "exception": {
                "type": type(error).__name__,
                "module": type(error).__module__,
                "message": str(error),
                "channel": getattr(error, "channel", None),
                "kind": getattr(error, "kind", None),
            },
        },
    )


def build_run_failure(
    config: ConcordiaNoPressConfig,
    detected_runtime: ConcordiaRuntimeStatus,
    runtime_path: str,
    runtimes: Mapping[str, ConcordiaSeatRuntime],
    failure: ConcordiaDecisionFailure,
    channel_metrics: dict[str, Any] | None = None,
) -> ConcordiaRunFailure:
    failure_with_c2 = ConcordiaDecisionFailure(
        failure.message,
        {
            **failure.snapshot,
            "c2_partial_state": build_c2_partial_state(runtimes),
        },
    )
    snapshot = run_failure_snapshot(
        config_snapshot=config_snapshot(config),
        runtime=runtime_payload(detected_runtime, runtime_path),
        agent_metadata=agent_metadata(config),
        failure=failure_with_c2,
        config=config,
    )
    if channel_metrics is not None:
        snapshot["channel_metrics"] = channel_metrics
    return ConcordiaRunFailure(str(failure), snapshot)


__all__ = ["budget_failure", "build_run_failure"]
