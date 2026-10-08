"""Deterrent legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .engine.events import EngineEvent
from .state import DETERRENT_SLOTS, GameState


def deterrent_actions(state: GameState, player_id: str) -> list[LegalAction]:
    player = state.players[player_id]
    actions = [
        build_action(player_id, ActionType.MODIFY_DETERRENT, "Skip deterrents", {})
    ]
    empty_slots = [
        index for index, card_id in enumerate(player.deterrents) if card_id is None
    ]
    for card_id in player.hand:
        for slot in empty_slots:
            actions.append(
                build_action(
                    player_id,
                    ActionType.MODIFY_DETERRENT,
                    f"Store {card_id}",
                    {"card": card_id, "to_slot": slot},
                )
            )
    for slot, card_id in enumerate(player.deterrents):
        if card_id is not None:
            actions.append(
                build_action(
                    player_id,
                    ActionType.MODIFY_DETERRENT,
                    f"Return {card_id}",
                    {"from_slot": slot},
                )
            )
    return actions


def apply_deterrent_action(
    state: GameState,
    action: LegalAction,
) -> list[EngineEvent]:
    player = state.players[action.player_id]
    payload = action.payload
    if not payload:
        return []
    if set(payload) == {"card", "to_slot"}:
        card_id = payload["card"]
        slot = payload["to_slot"]
        if (
            not isinstance(card_id, str)
            or not _valid_slot(slot)
            or card_id not in player.hand
            or player.deterrents[slot] is not None
        ):
            return []
        player.hand.remove(card_id)
        player.deterrents[slot] = card_id
        return []
    if set(payload) == {"from_slot"}:
        slot = payload["from_slot"]
        if not _valid_slot(slot) or player.deterrents[slot] is None:
            return []
        player.hand.append(str(player.deterrents[slot]))
        player.deterrents[slot] = None
        return []
    return []


def _valid_slot(value: object) -> bool:
    return type(value) is int and 0 <= value < DETERRENT_SLOTS


__all__ = ["apply_deterrent_action", "deterrent_actions"]
