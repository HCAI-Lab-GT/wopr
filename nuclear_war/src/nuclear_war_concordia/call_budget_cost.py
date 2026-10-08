"""Shared study-wide cost reservations for channel budgets."""

from __future__ import annotations

import math
import threading
from typing import Any

from .call_budget_errors import ChannelRequestBudgetExceeded

_COST_LOCK = threading.RLock()


def reserve_cost(budget: Any) -> None:
    with _COST_LOCK:
        amount = budget.max_cost_per_request_usd
        if amount is None:
            return
        proposed = budget.reserved_cost_usd + amount
        study_proposed = study_cost(budget, "reserved_cost_usd") + amount
        if budget.max_cost_usd is not None and study_proposed > budget.max_cost_usd:
            error = ChannelRequestBudgetExceeded(
                budget.active_channel or "unknown",
                round(study_proposed * 1_000_000),
                round(budget.max_cost_usd * 1_000_000),
                "cost",
            )
            error.partial_metrics = budget.snapshot()
            raise error
        budget.reserved_cost_usd = proposed
        if budget.shared_cost_state is not None:
            budget.shared_cost_state["reserved_cost_usd"] = study_proposed


def record_actual_cost(budget: Any, value: float | None) -> None:
    with _COST_LOCK:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return
        amount = float(value)
        if amount < 0 or not math.isfinite(amount):
            raise ValueError("Provider-reported actual cost is invalid")
        budget.actual_cost_usd += amount
        if budget.shared_cost_state is not None:
            budget.shared_cost_state["actual_cost_usd"] = (
                study_cost(budget, "actual_cost_usd") + amount
            )
        study_actual = study_cost(budget, "actual_cost_usd")
        if budget.max_cost_usd is not None and study_actual > budget.max_cost_usd:
            error = ChannelRequestBudgetExceeded(
                budget.active_channel or "unknown",
                round(study_actual * 1_000_000),
                round(budget.max_cost_usd * 1_000_000),
                "cost",
            )
            error.partial_metrics = budget.snapshot()
            raise error


def study_cost(budget: Any, field: str) -> float:
    with _COST_LOCK:
        if budget.shared_cost_state is not None:
            return float(budget.shared_cost_state.get(field, 0.0))
        return float(getattr(budget, field))


__all__ = ["record_actual_cost", "reserve_cost", "study_cost"]
