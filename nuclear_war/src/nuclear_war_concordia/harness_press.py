"""Press coordinator construction for the Concordia harness."""

from __future__ import annotations

from collections.abc import Mapping

from .config import ConcordiaNoPressConfig
from .harness_seat_runtime import ConcordiaSeatRuntime
from .press_coordinator import PressCoordinator


def build_press_coordinator(
    config: ConcordiaNoPressConfig,
    runtimes: Mapping[str, ConcordiaSeatRuntime],
    press_traces: list[dict[str, object]],
) -> PressCoordinator:
    mode = config.press.mode
    passes = config.press.passes if mode in {"multi_turn_public", "full_press"} else 1
    return PressCoordinator(
        speakers=list(config.seats.keys()),
        clients={pid: runtime.spokesperson_client for pid, runtime in runtimes.items()},
        identities={
            pid: dict(runtime.spokesperson_identity)
            for pid, runtime in runtimes.items()
        },
        press_sink=press_traces,
        max_retries=1,
        passes=passes,
        mode=mode,
    )
