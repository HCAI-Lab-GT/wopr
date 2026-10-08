"""Fake client for no-network scorecard tests."""

from __future__ import annotations

from nuclear_war_agents import FirstLegalLLMClient, LLMCompletion


class ScorecardFakeClient:
    def __init__(self) -> None:
        self._first_legal = FirstLegalLLMClient()

    def complete(self, prompt: str) -> str | LLMCompletion:
        if prompt.startswith("Respond only with this JSON:"):
            return LLMCompletion('{"action_id": "smoke:test"}')
        return self._first_legal.complete(prompt)


__all__ = ["ScorecardFakeClient"]
