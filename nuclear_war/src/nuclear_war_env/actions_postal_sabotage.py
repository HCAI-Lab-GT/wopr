"""Postal sabotage legal action helpers."""

from __future__ import annotations

from typing import Any

from .action_models import ActionType, LegalAction, build_action
from .cards import CardCategory
from .engine.events import EngineEvent
from .state import GameState


def sabotage_legal_actions(state: GameState, player_id: str) -> list[LegalAction]:
    saboteurs = _hand_saboteurs(state, player_id)
    if not saboteurs:
        return []
    actions: list[LegalAction] = []
    for card_id in saboteurs:
        for target_id, target in state.players.items():
            if target_id == player_id or not target.alive:
                continue
            actions.extend(
                _target_actions(player_id, card_id, target_id, target.pending_orders)
            )
    return actions


def apply_sabotage_action(state: GameState, action: LegalAction) -> list[EngineEvent]:
    card_id = str(action.payload["card"])
    target_id = str(action.payload["target"])
    order = {key: value for key, value in action.payload.items() if key != "card"}
    state.players[action.player_id].discard_from_hand(card_id)
    state.players[action.player_id].pending_orders.setdefault("sabotage", []).append(
        order
    )
    return [
        EngineEvent(
            "postal_sabotage_ordered",
            action.player_id,
            card_id,
            {"target": target_id},
        )
    ]


def _target_actions(
    player_id: str,
    card_id: str,
    target_id: str,
    orders: dict[str, Any],
) -> list[LegalAction]:
    actions = _launch_actions(player_id, card_id, target_id, orders)
    actions.extend(
        _order_actions(
            player_id,
            card_id,
            target_id,
            orders,
            "atomic_cannon",
            "cannon",
            "atomic_cannon",
        )
    )
    actions.extend(
        _order_actions(
            player_id,
            card_id,
            target_id,
            orders,
            "killer_satellite_launch",
            "satellite",
            "satellite",
        )
    )
    actions.extend(
        _order_actions(
            player_id,
            card_id,
            target_id,
            orders,
            "space_shuttle_attack",
            "shuttle",
            "shuttle",
        )
    )
    return actions


def _launch_actions(
    player_id: str,
    card_id: str,
    target_id: str,
    orders: dict[str, Any],
) -> list[LegalAction]:
    launches = orders.get("launches", {})
    if not isinstance(launches, dict):
        return []
    return [
        _build(player_id, card_id, target_id, "delivery", str(delivery_id))
        for delivery_id in launches
    ]


def _order_actions(
    player_id: str,
    card_id: str,
    target_id: str,
    orders: dict[str, Any],
    order_key: str,
    id_key: str,
    target_key: str,
) -> list[LegalAction]:
    pending = orders.get(order_key, [])
    if not isinstance(pending, list):
        return []
    return [
        _build(player_id, card_id, target_id, target_key, str(order[id_key]))
        for order in pending
        if id_key in order
    ]


def _build(
    player_id: str, card_id: str, target_id: str, target_key: str, target_value: str
) -> LegalAction:
    return build_action(
        player_id,
        ActionType.POSTAL_SABOTAGE,
        f"Sabotage {target_value}",
        {"card": card_id, "target": target_id, target_key: target_value},
    )


def _hand_saboteurs(state: GameState, player_id: str) -> list[str]:
    return [
        card_id
        for card_id in state.players[player_id].hand
        if state.card_by_id(card_id).category is CardCategory.SPECIAL
        and state.card_by_id(card_id).metadata.get("postal_effect") == "sabotage"
    ]


__all__ = ["apply_sabotage_action", "sabotage_legal_actions"]
