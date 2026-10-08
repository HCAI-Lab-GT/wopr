"""Postal anti-missile defense legal action helpers.

Postal rules resolve interception through conditional orders submitted before
launches are known ("Intercept anything ... at me"). A defense order commits an
anti-missile card from hand for the current turn; the card is only discarded
when it actually intercepts, and unused orders expire at the end of the turn.
"""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .cards import CardCategory
from .engine.events import EngineEvent
from .state import GameState


def defense_legal_actions(state: GameState, player_id: str) -> list[LegalAction]:
    player = state.players[player_id]
    queued = player.pending_orders.get("defense")
    queued_ids = set(queued) if isinstance(queued, list) else set()
    actions: list[LegalAction] = []
    for card_id in player.hand:
        if state.card_by_id(card_id).category is not CardCategory.ANTIMISSILE:
            continue
        if card_id in queued_ids:
            continue
        actions.append(
            build_action(
                player_id,
                ActionType.POSTAL_DEFENSE,
                f"Hold {card_id} to intercept incoming launches",
                {"card": card_id},
            )
        )
    return actions


def apply_defense_action(state: GameState, action: LegalAction) -> list[EngineEvent]:
    card_id = str(action.payload["card"])
    queue = state.players[action.player_id].pending_orders.setdefault("defense", [])
    if card_id not in queue:
        queue.append(card_id)
    return [EngineEvent("postal_defense_ordered", action.player_id, card_id)]


__all__ = ["apply_defense_action", "defense_legal_actions"]
