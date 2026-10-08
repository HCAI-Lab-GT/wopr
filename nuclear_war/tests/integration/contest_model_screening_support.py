"""Non-billable payload runners used by screening integration tests."""

from __future__ import annotations

from typing import Any

from nuclear_war_concordia.config import load_concordia_no_press_config
from nuclear_war_concordia.harness import run_concordia_no_press_game


def offline_runner(
    payload: dict[str, object], *_: object, **__: object
) -> dict[str, Any]:
    seats = payload["seats"]
    assert isinstance(seats, dict)
    for seat in seats.values():
        assert isinstance(seat, dict)
        seat["agent"] = "concordia_first_legal"
        seat.pop("client", None)
    return run_concordia_no_press_game(load_concordia_no_press_config(payload))


def one_failure_runner():
    failed = False

    def runner(payload: dict[str, object], *_: object, **__: object) -> dict[str, Any]:
        nonlocal failed
        if not failed:
            failed = True
            raise ValueError("screening fixture failure")
        return offline_runner(payload)

    return runner


__all__ = ["offline_runner", "one_failure_runner"]
