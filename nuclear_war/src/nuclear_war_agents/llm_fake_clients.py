"""Deterministic fake model clients for no-press LLM harness tests."""

from __future__ import annotations

import json


class FirstLegalLLMClient:
    def complete(self, prompt: str) -> str:
        return json.dumps({"action_id": _first_legal_action_id(prompt)})


def _first_legal_action_id(prompt: str) -> str:
    in_action_ids = False
    for line in prompt.splitlines():
        if line == "Legal action ids:":
            in_action_ids = True
            continue
        if in_action_ids and not line:
            break
        if in_action_ids and line.startswith("- "):
            return line[2:]
    raise ValueError("Prompt does not include legal action ids")


__all__ = ["FirstLegalLLMClient"]
