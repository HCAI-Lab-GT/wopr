"""Postal cruise missile launch legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .cards import CardCategory
from .engine.events import EngineEvent
from .integer_validation import positive_int_or_zero
from .state import GameState


def cruise_launch_actions(state: GameState, player_id: str) -> list[LegalAction]:
    result: list[LegalAction] = []
    specials = _hand_cards_with_effect(state, player_id, "cruise_missile")
    warheads = _hand_warheads(state, player_id)
    for special_id in specials:
        for warhead_id, _payload in warheads:
            for target_id, target in state.players.items():
                if target_id == player_id or not target.alive:
                    continue
                result.append(
                    build_action(
                        player_id,
                        ActionType.POSTAL_CRUISE_LAUNCH,
                        f"Launch cruise missile at {target_id}",
                        {
                            "card": special_id,
                            "target": target_id,
                            "warhead": warhead_id,
                        },
                    )
                )
    return result


def apply_cruise_launch_action(
    state: GameState, action: LegalAction
) -> list[EngineEvent]:
    if action.action_type is not ActionType.POSTAL_CRUISE_LAUNCH:
        return []
    card_id = str(action.payload["card"])
    target_id = str(action.payload["target"])
    warhead_id = str(action.payload["warhead"])
    player = state.players[action.player_id]
    payload = _warhead_payload(state, warhead_id)
    player.discard_from_hand(card_id)
    player.discard_from_hand(warhead_id)
    player.pending_orders.setdefault("cruise_launch", []).append(
        {"missile": card_id, "target": target_id, "yield": payload}
    )
    return [
        EngineEvent(
            "postal_cruise_launch_ordered",
            action.player_id,
            card_id,
            {"target": target_id, "yield": payload},
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


def _hand_warheads(state: GameState, player_id: str) -> list[tuple[str, int]]:
    result: list[tuple[str, int]] = []
    for card_id in state.players[player_id].hand:
        card = state.card_by_id(card_id)
        if card.category is not CardCategory.WARHEAD:
            continue
        payload = _warhead_payload(state, card_id)
        if payload > 0:
            result.append((card_id, payload))
    return result


def _warhead_payload(state: GameState, warhead_id: str) -> int:
    card = state.card_by_id(warhead_id)
    value = card.value or card.metadata.get("yield_megatons", 0)
    return positive_int_or_zero(value)


__all__ = ["apply_cruise_launch_action", "cruise_launch_actions"]
