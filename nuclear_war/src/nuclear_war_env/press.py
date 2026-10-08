"""Press-mode scope guards."""

from __future__ import annotations

PRESS_DEFERRED_MESSAGE = "Postal press is deferred until after v1"
PRESS_FALSE_MESSAGE = "Press must be false for v1"


def reject_press_mode(press: object) -> None:
    if press is True:
        raise ValueError(PRESS_DEFERRED_MESSAGE)
    if press is not False:
        raise ValueError(PRESS_FALSE_MESSAGE)


__all__ = ["PRESS_DEFERRED_MESSAGE", "PRESS_FALSE_MESSAGE", "reject_press_mode"]
