"""Postal submarine setup legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .cards import CardCategory
from .engine.events import EngineEvent
from .engine.postal.submarine_setup import VALID_SUBMARINE_WARHEADS
from .integer_validation import positive_int_or_zero
from .state import GameState


def submarine_setup_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions = _launch_actions(state, player_id)
    actions.extend(_reload_actions(state, player_id))
    return actions


def apply_submarine_setup_action(
    state: GameState, action: LegalAction
) -> list[EngineEvent]:
    if action.action_type is ActionType.POSTAL_SUBMARINE_LAUNCH:
        return _queue_setup(state, action, "submarine_launch", "card", "launch")
    if action.action_type is ActionType.POSTAL_SUBMARINE_RELOAD:
        return _queue_setup(state, action, "submarine_reload", "submarine", "reload")
    return []


def _launch_actions(state: GameState, player_id: str) -> list[LegalAction]:
    result: list[LegalAction] = []
    specials = _hand_cards_with_effect(state, player_id, "submarine")
    warheads = _valid_hand_warheads(state, player_id)
    for special_id in specials:
        for warhead_id, _payload in warheads:
            result.extend(_targeted_actions(state, player_id, special_id, warhead_id))
    return result


def _reload_actions(state: GameState, player_id: str) -> list[LegalAction]:
    submarines = state.players[player_id].pending_orders.get("submarine_states", {})
    if not isinstance(submarines, dict):
        return []
    result: list[LegalAction] = []
    warheads = _valid_hand_warheads(state, player_id)
    for submarine_id, submarine in submarines.items():
        if not isinstance(submarine, dict) or submarine.get("status") != "in_port":
            continue
        for warhead_id, _payload in warheads:
            result.extend(
                _targeted_actions(state, player_id, str(submarine_id), warhead_id, True)
            )
    return result


def _targeted_actions(
    state: GameState,
    player_id: str,
    submarine_id: str,
    warhead_id: str,
    reload_order: bool = False,
) -> list[LegalAction]:
    result: list[LegalAction] = []
    action_type = (
        ActionType.POSTAL_SUBMARINE_RELOAD
        if reload_order
        else ActionType.POSTAL_SUBMARINE_LAUNCH
    )
    id_key = "submarine" if reload_order else "card"
    for target_id, target in state.players.items():
        if target_id == player_id or not target.alive:
            continue
        result.append(
            build_action(
                player_id,
                action_type,
                f"Send submarine to {target_id}",
                {id_key: submarine_id, "target": target_id, "warhead": warhead_id},
            )
        )
    return result


def _queue_setup(
    state: GameState,
    action: LegalAction,
    order_key: str,
    id_key: str,
    label: str,
) -> list[EngineEvent]:
    submarine_id = str(action.payload[id_key])
    target_id = str(action.payload["target"])
    warhead_id = str(action.payload["warhead"])
    payload = _warhead_payload(state, warhead_id)
    player = state.players[action.player_id]
    if id_key == "card":
        player.discard_from_hand(submarine_id)
    player.discard_from_hand(warhead_id)
    player.pending_orders.setdefault(order_key, []).append(
        {"submarine": submarine_id, "target": target_id, "warhead_yield": payload}
    )
    return [
        EngineEvent(
            f"postal_submarine_{label}_ordered",
            action.player_id,
            submarine_id,
            {"target": target_id, "warhead_yield": payload},
        )
    ]


def _hand_cards_with_effect(
    state: GameState, player_id: str, postal_effect: str
) -> list[str]:
    result: list[str] = []
    for card_id in state.players[player_id].hand:
        card = state.card_by_id(card_id)
        if (
            card.category is CardCategory.SPECIAL
            and card.metadata.get("postal_effect") == postal_effect
        ):
            result.append(card_id)
    return result


def _valid_hand_warheads(state: GameState, player_id: str) -> list[tuple[str, int]]:
    result: list[tuple[str, int]] = []
    for card_id in state.players[player_id].hand:
        payload = _warhead_payload(state, card_id)
        if payload in VALID_SUBMARINE_WARHEADS:
            result.append((card_id, payload))
    return result


def _warhead_payload(state: GameState, warhead_id: str) -> int:
    card = state.card_by_id(warhead_id)
    if card.category is not CardCategory.WARHEAD:
        return 0
    value = card.value or card.metadata.get("yield_megatons", 0)
    return positive_int_or_zero(value)


__all__ = ["apply_submarine_setup_action", "submarine_setup_actions"]
