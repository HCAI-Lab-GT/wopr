"""Shared provider metadata helper tests."""

from __future__ import annotations

from nuclear_war_agents import LLMCompletion
from nuclear_war_concordia.provider_metadata import provider_metadata


def test_provider_metadata_aggregates_completions() -> None:
    completions = [
        LLMCompletion(
            raw_response="a",
            provider_latency_ms=10,
            provider_cost=0.01,
            provider_usage={"total_tokens": 5},
            provider_label="together",
            provider_model="demo-1",
        )
    ]

    metadata = provider_metadata(completions)

    assert metadata == {
        "provider_latency_ms": 10,
        "provider_cost": 0.01,
        "provider_usage": {"total_tokens": 5},
        "provider_label": "together",
        "provider_model": "demo-1",
    }


def test_provider_metadata_empty_completions() -> None:
    metadata = provider_metadata([])

    assert metadata["provider_label"] is None
    assert metadata["provider_latency_ms"] is None
