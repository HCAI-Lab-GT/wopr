"""Response parsing for Concordia-backed WOPR decisions."""

from __future__ import annotations

from collections.abc import Iterable

from nuclear_war_agents.llm_response import parse_llm_response

from .types import ParsedConcordiaDecision


def parse_concordia_response(
    raw_response: str,
    legal_action_ids: Iterable[str] = (),
) -> ParsedConcordiaDecision:
    parsed = parse_llm_response(raw_response, legal_action_ids)
    return ParsedConcordiaDecision(
        parsed.action_id,
        parsed.rationale,
    )
