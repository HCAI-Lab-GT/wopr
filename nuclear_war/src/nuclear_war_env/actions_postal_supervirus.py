"""Postal Supervirus legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .cards import CardCategory
from .engine.events import EngineEvent
from .state import GameState


def supervirus_legal_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions = _start_actions(state, player_id)
    infection = state.players[player_id].pending_orders.get("supervirus")
    if not isinstance(infection, dict):
        return actions
    source_id = str(infection.get("source", ""))
    for target_id, target in state.players.items():
        if not _can_pass(state, player_id, target_id, source_id) or not target.alive:
            continue
        actions.append(
            build_action(
                player_id,
                ActionType.POSTAL_SUPERVIRUS_PASS,
                f"Pass Supervirus to {target_id}",
                {"target": target_id},
            )
        )
    return actions


def apply_supervirus_action(state: GameState, action: LegalAction) -> list[EngineEvent]:
    if action.action_type is ActionType.POSTAL_SUPERVIRUS_START:
        return _queue_start(state, action)
    if action.action_type is not ActionType.POSTAL_SUPERVIRUS_PASS:
        return []
    target_id = str(action.payload["target"])
    state.players[action.player_id].pending_orders["supervirus_pass"] = {
        "target": target_id
    }
    return [
        EngineEvent(
            "postal_supervirus_pass_ordered",
            action.player_id,
            None,
            {"target": target_id},
        )
    ]


def _start_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions: list[LegalAction] = []
    for card_id in state.players[player_id].hand:
        card = state.card_by_id(card_id)
        if (
            card.category is not CardCategory.SPECIAL
            or card.metadata.get("postal_effect") != "supervirus"
        ):
            continue
        for target_id, target in state.players.items():
            if target_id == player_id or not target.alive:
                continue
            if _is_immune(state, target_id):
                continue
            actions.append(
                build_action(
                    player_id,
                    ActionType.POSTAL_SUPERVIRUS_START,
                    f"Start Supervirus in {target_id}",
                    {"card": card_id, "target": target_id},
                )
            )
    return actions


def _queue_start(state: GameState, action: LegalAction) -> list[EngineEvent]:
    card_id = str(action.payload["card"])
    target_id = str(action.payload["target"])
    state.players[action.player_id].discard_from_hand(card_id)
    state.players[action.player_id].pending_orders["supervirus_start"] = {
        "card": card_id,
        "target": target_id,
    }
    return [
        EngineEvent(
            "postal_supervirus_start_ordered",
            action.player_id,
            card_id,
            {"target": target_id},
        )
    ]


def _is_immune(state: GameState, target_id: str) -> bool:
    return bool(state.players[target_id].pending_orders.get("supervirus_immunity"))


def _can_pass(
    state: GameState,
    holder_id: str,
    target_id: str,
    source_id: str,
) -> bool:
    if target_id == holder_id:
        return False
    if _is_immune(state, target_id):
        return False
    alive_count = sum(player.alive for player in state.players.values())
    return alive_count <= 2 or target_id != source_id


__all__ = ["apply_supervirus_action", "supervirus_legal_actions"]
