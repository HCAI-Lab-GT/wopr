"""Errors emitted before or after a guarded provider request."""

from __future__ import annotations

from typing import Any


class ChannelRequestBudgetExceeded(RuntimeError):
    channel_budget_exceeded = True

    def __init__(self, channel: str, observed: int, cap: int, kind: str) -> None:
        self.channel, self.observed, self.cap, self.kind = channel, observed, cap, kind
        self.partial_metrics: dict[str, Any] | None = None
        super().__init__(f"{channel} {kind} cap exceeded: {observed} > {cap}")


__all__ = ["ChannelRequestBudgetExceeded"]
