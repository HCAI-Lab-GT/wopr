"""Agent action validation helpers."""

from __future__ import annotations

from .actions import LegalAction


def require_legal_agent_action(
    selected: LegalAction,
    legal_actions: list[LegalAction],
) -> LegalAction:
    if selected in legal_actions:
        return selected
    raise ValueError(
        f"Agent selected illegal action: {selected.action_id} "
        f"for player {selected.player_id}"
    )


__all__ = ["require_legal_agent_action"]
