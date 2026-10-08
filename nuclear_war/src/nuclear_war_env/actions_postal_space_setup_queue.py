"""Postal space equipment setup action application helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction
from .cards import CardCategory
from .engine.events import EngineEvent
from .integer_validation import positive_int_or_zero
from .state import GameState


def apply_space_setup_action(
    state: GameState, action: LegalAction
) -> list[EngineEvent]:
    if action.action_type is ActionType.POSTAL_SPACE_PLATFORM_LAUNCH:
        return _queue_platform_launch(state, action)
    if action.action_type is ActionType.POSTAL_SPACE_SHUTTLE_RELOAD:
        return _queue_shuttle_reload(state, action)
    if action.action_type is ActionType.POSTAL_SPACE_SHUTTLE_ATTACK:
        return _queue_shuttle_attack(state, action)
    if action.action_type is ActionType.POSTAL_KILLER_SATELLITE_LAUNCH:
        return _queue_satellite_launch(state, action)
    return []


def _queue_platform_launch(state: GameState, action: LegalAction) -> list[EngineEvent]:
    card_id = str(action.payload["card"])
    warheads = _consume_warheads(state, action)
    _discard_card(state, action.player_id, card_id)
    state.players[action.player_id].pending_orders.setdefault(
        "space_platform_launch", []
    ).append({"platform": card_id, "warheads": warheads})
    return [
        EngineEvent("postal_space_platform_launch_ordered", action.player_id, card_id)
    ]


def _queue_shuttle_reload(state: GameState, action: LegalAction) -> list[EngineEvent]:
    card_id = str(action.payload["card"])
    platform_id = str(action.payload["platform"])
    warheads = _consume_warheads(state, action)
    _discard_card(state, action.player_id, card_id)
    state.players[action.player_id].pending_orders.setdefault(
        "space_shuttle_reload", []
    ).append({"platform": platform_id, "warheads": warheads})
    return [
        EngineEvent("postal_space_shuttle_reload_ordered", action.player_id, card_id)
    ]


def _queue_shuttle_attack(state: GameState, action: LegalAction) -> list[EngineEvent]:
    card_id = str(action.payload["card"])
    warhead_id = str(action.payload["warhead"])
    target_id = str(action.payload["target"])
    payload = _warhead_payload(state, warhead_id)
    _discard_card(state, action.player_id, card_id)
    _discard_card(state, action.player_id, warhead_id)
    state.players[action.player_id].pending_orders.setdefault(
        "space_shuttle_attack", []
    ).append({"shuttle": card_id, "target": target_id, "warheads": [payload]})
    return [
        EngineEvent("postal_space_shuttle_attack_ordered", action.player_id, card_id)
    ]


def _queue_satellite_launch(state: GameState, action: LegalAction) -> list[EngineEvent]:
    card_id = str(action.payload["card"])
    _discard_card(state, action.player_id, card_id)
    state.players[action.player_id].pending_orders.setdefault(
        "killer_satellite_launch", []
    ).append({"satellite": card_id})
    return [
        EngineEvent("postal_killer_satellite_launch_ordered", action.player_id, card_id)
    ]


def _consume_warheads(state: GameState, action: LegalAction) -> list[int]:
    warhead_ids = [str(card_id) for card_id in action.payload["warheads"]]
    for card_id in warhead_ids:
        _discard_card(state, action.player_id, card_id)
    return [_warhead_payload(state, card_id) for card_id in warhead_ids]


def _warhead_payload(state: GameState, card_id: str) -> int:
    card = state.card_by_id(card_id)
    if card.category is not CardCategory.WARHEAD:
        return 0
    value = card.value or card.metadata.get("yield_megatons", 0)
    return positive_int_or_zero(value)


def _discard_card(state: GameState, player_id: str, card_id: str) -> None:
    state.players[player_id].discard_from_hand(card_id)


__all__ = ["apply_space_setup_action"]
