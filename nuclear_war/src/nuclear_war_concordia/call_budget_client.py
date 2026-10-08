"""Channel-specific views over one Concordia client."""

from __future__ import annotations

from typing import Any

from .call_budget_state import ChannelCallBudget


class ChannelScopedConcordiaClient:
    def __init__(self, client: Any, budget: ChannelCallBudget, channel: str) -> None:
        self.base_client = getattr(client, "base_client", client)
        self.budget = budget
        self.channel = channel

    def complete(self, scene_text: str) -> Any:
        self.budget.reserve(self.channel)
        if not _has_transport_guard(self.base_client):
            self.budget.reserve_transport(self.channel)
        previous = self.budget.active_channel
        self.budget.active_channel = self.channel
        try:
            result = self.base_client.complete(scene_text)
            self.budget.record_actual_cost(getattr(result, "provider_cost", None))
            return result
        finally:
            self.budget.active_channel = previous

    def __getattr__(self, name: str) -> Any:
        return getattr(self.base_client, name)


def _has_transport_guard(client: Any) -> bool:
    if getattr(client, "request_guard", None) is not None:
        return True
    model = getattr(client, "model", None)
    return getattr(getattr(model, "client", None), "request_guard", None) is not None


__all__ = ["ChannelScopedConcordiaClient"]
