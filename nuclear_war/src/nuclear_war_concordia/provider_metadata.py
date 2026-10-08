"""Shared provider metadata aggregation for Concordia traces."""

from __future__ import annotations

from typing import Any

from nuclear_war_agents import LLMCompletion
from nuclear_war_agents import llm_completion as llm_meta


def provider_metadata(completions: list[LLMCompletion]) -> dict[str, Any]:
    return {
        "provider_latency_ms": llm_meta.total_provider_latency(completions),
        "provider_cost": llm_meta.total_provider_cost(completions),
        "provider_usage": llm_meta.total_provider_usage(completions),
        "provider_label": llm_meta.first_provider_label(completions),
        "provider_model": llm_meta.first_provider_model(completions),
    }
