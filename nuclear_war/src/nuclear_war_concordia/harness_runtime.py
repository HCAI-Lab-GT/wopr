"""Runtime path selection for Concordia no-press harness runs."""

from __future__ import annotations

from .config import ConcordiaNoPressConfig
from .config_constants import NATIVE_AGENTS
from .types import ConcordiaRuntimeStatus

STYLE_RUNTIME_PATH = "concordia_style_fallback"
NATIVE_RUNTIME_PATH = "concordia_runtime"


def execution_runtime_path(
    config: ConcordiaNoPressConfig,
    detected_runtime: ConcordiaRuntimeStatus,
) -> str:
    native_count = sum(seat.agent in NATIVE_AGENTS for seat in config.seats.values())
    if native_count and native_count != len(config.seats):
        raise ValueError("Native Concordia seats cannot mix with fallback seats")
    if native_count:
        _require_detected_runtime(detected_runtime)
        if config.runtime == STYLE_RUNTIME_PATH:
            raise ValueError("Native Concordia seats require concordia_runtime")
        return NATIVE_RUNTIME_PATH
    if config.runtime == NATIVE_RUNTIME_PATH:
        raise ValueError("concordia_runtime requires native Concordia seats")
    return STYLE_RUNTIME_PATH


def _require_detected_runtime(detected_runtime: ConcordiaRuntimeStatus) -> None:
    if (
        detected_runtime.runtime_path != NATIVE_RUNTIME_PATH
        or not detected_runtime.available
    ):
        raise ValueError("Native Concordia seats require concordia_runtime")
