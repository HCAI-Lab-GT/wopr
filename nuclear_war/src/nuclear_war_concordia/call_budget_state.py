"""Logical-call, provider-attempt, token, and spend accounting."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from .call_budget_cost import record_actual_cost, reserve_cost, study_cost
from .call_budget_errors import ChannelRequestBudgetExceeded
from .call_budget_restore import restore_initial_metrics


@dataclass
class ChannelCallBudget:
    c2_cap: int
    press_cap: int
    provider_attempt_multiplier: int = 1
    input_tokens_bound: int | None = None
    max_cost_usd: float | None = None
    max_cost_per_request_usd: float | None = None
    initial_metrics: dict[str, Any] | None = None
    shared_cost_state: dict[str, float] | None = None
    c2_calls: int = 0
    press_calls: int = 0
    c2_provider_attempts: int = 0
    press_provider_attempts: int = 0
    reserved_cost_usd: float = 0.0
    actual_cost_usd: float = 0.0
    active_channel: str | None = None

    def __post_init__(self) -> None:
        if self.provider_attempt_multiplier < 1:
            raise ValueError("provider_attempt_multiplier must be positive")
        restore_initial_metrics(self)

    def reserve(self, channel: str) -> None:
        self._increment(channel, "calls", self._cap(channel))

    def reserve_transport(self, channel: str) -> None:
        self._increment(
            channel,
            "provider_attempts",
            self._cap(channel) * self.provider_attempt_multiplier,
        )

    def reserve_transport_active(self) -> None:
        if self.active_channel is None:
            raise RuntimeError("A channel must be active before a provider request")
        self.reserve_transport(self.active_channel)

    def validate_prompt(self, prompt: str) -> None:
        if self.input_tokens_bound is None:
            return
        estimated = max(1, (len(prompt) + 3) // 4)
        if estimated > self.input_tokens_bound:
            error = ChannelRequestBudgetExceeded(
                self.active_channel or "unknown",
                estimated,
                self.input_tokens_bound,
                "input-token",
            )
            error.partial_metrics = self.snapshot()
            raise error

    def reserve_cost(self) -> None:
        reserve_cost(self)

    def record_actual_cost(self, value: float | None) -> None:
        record_actual_cost(self, value)

    def guard(self, channel: str) -> Callable[[], None]:
        return lambda: self.reserve(channel)

    def snapshot(self) -> dict[str, Any]:
        return {
            "c2": self._channel_snapshot("c2"),
            "press": self._channel_snapshot("press"),
            "reserved_cost_usd": round(self.reserved_cost_usd, 9),
            "actual_cost_usd": round(self.actual_cost_usd, 9),
            "study_reserved_cost_usd": round(
                study_cost(self, "reserved_cost_usd"),
                9,
            ),
            "study_actual_cost_usd": round(
                study_cost(self, "actual_cost_usd"),
                9,
            ),
        }

    def _channel_snapshot(self, channel: str) -> dict[str, int]:
        calls = self._calls(channel)
        attempts = self._provider_attempts(channel)
        return {
            "call_count": calls,
            "provider_attempt_count": attempts,
            "transport_retry_count": max(0, attempts - calls),
        }

    def _cap(self, channel: str) -> int:
        if channel not in {"c2", "press"}:
            raise ValueError(f"Unknown request-budget channel: {channel}")
        return getattr(self, f"{channel}_cap")

    def _calls(self, channel: str) -> int:
        return int(getattr(self, f"{channel}_calls"))

    def _provider_attempts(self, channel: str) -> int:
        return int(getattr(self, f"{channel}_provider_attempts"))

    def _set(self, channel: str, suffix: str, value: int) -> None:
        setattr(self, f"{channel}_{suffix}", value)

    def _increment(self, channel: str, suffix: str, cap: int) -> None:
        current = (
            self._calls(channel)
            if suffix == "calls"
            else self._provider_attempts(channel)
        )
        observed = current + 1
        if observed > cap:
            error = ChannelRequestBudgetExceeded(
                channel, observed, cap, suffix.replace("_", "-")
            )
            error.partial_metrics = self.snapshot()
            raise error
        if suffix == "provider_attempts":
            self.reserve_cost()
        self._set(channel, suffix, observed)


def partial_metrics(error: BaseException) -> dict[str, Any] | None:
    value = getattr(error, "partial_metrics", None)
    return value if isinstance(value, dict) else None


__all__ = ["ChannelCallBudget", "ChannelRequestBudgetExceeded", "partial_metrics"]
