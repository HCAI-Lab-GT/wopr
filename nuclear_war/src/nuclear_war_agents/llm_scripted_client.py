"""Deterministic scripted LLM client for tests and local harness runs."""

from __future__ import annotations

from dataclasses import dataclass

from .llm_types import LLMCompletion


@dataclass
class ScriptedLLMClient:
    responses: list[str | LLMCompletion]
    index: int = 0

    def complete(self, prompt: str) -> str | LLMCompletion:
        if not self.responses:
            raise ValueError("ScriptedLLMClient requires at least one response")
        response = self.responses[min(self.index, len(self.responses) - 1)]
        self.index += 1
        return response


__all__ = ["ScriptedLLMClient"]
