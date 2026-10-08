"""Postal atomic cannon legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .cards import CardCategory
from .engine.events import EngineEvent
from .state import GameState


def atomic_legal_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions = _setup_actions(state, player_id)
    cannons = state.players[player_id].pending_orders.get("atomic_cannons", {})
    if not isinstance(cannons, dict):
        return actions
    for cannon_id, cannon in cannons.items():
        if not isinstance(cannon, dict) or cannon.get("status") != "ready":
            continue
        actions.extend(_fire_actions(state, player_id, str(cannon_id), cannon))
        actions.extend(_reposition_actions(state, player_id, str(cannon_id), cannon))
    return actions


def apply_atomic_action(state: GameState, action: LegalAction) -> list[EngineEvent]:
    if action.action_type is ActionType.POSTAL_ATOMIC_CANNON_SETUP:
        return _queue_setup(state, action)
    if action.action_type is ActionType.POSTAL_ATOMIC_CANNON_FIRE:
        return _queue_fire(state, action)
    if action.action_type is ActionType.POSTAL_ATOMIC_CANNON_REPOSITION:
        return _queue_reposition(state, action)
    return []


def _setup_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions: list[LegalAction] = []
    for card_id in state.players[player_id].hand:
        card = state.card_by_id(card_id)
        if (
            card.category is not CardCategory.SPECIAL
            or card.metadata.get("postal_effect") != "atomic_cannon"
        ):
            continue
        for target_id, target in state.players.items():
            if target_id == player_id or not target.alive:
                continue
            actions.append(
                build_action(
                    player_id,
                    ActionType.POSTAL_ATOMIC_CANNON_SETUP,
                    f"Set up atomic cannon against {target_id}",
                    {"card": card_id, "target": target_id},
                )
            )
    return actions


def _fire_actions(
    state: GameState, player_id: str, cannon_id: str, cannon: dict
) -> list[LegalAction]:
    target_id = cannon.get("target")
    if target_id not in state.players or not state.players[str(target_id)].alive:
        return []
    result: list[LegalAction] = []
    for card_id in state.players[player_id].hand:
        card = state.card_by_id(card_id)
        if card.category is not CardCategory.WARHEAD or card.value != 10:
            continue
        result.append(
            build_action(
                player_id,
                ActionType.POSTAL_ATOMIC_CANNON_FIRE,
                f"Fire atomic cannon {cannon_id}",
                {"cannon": cannon_id, "warhead": card_id},
            )
        )
    return result


def _reposition_actions(
    state: GameState, player_id: str, cannon_id: str, cannon: dict
) -> list[LegalAction]:
    result: list[LegalAction] = []
    current_target = cannon.get("target")
    for target_id, target in state.players.items():
        if target_id == player_id or target_id == current_target or not target.alive:
            continue
        result.append(
            build_action(
                player_id,
                ActionType.POSTAL_ATOMIC_CANNON_REPOSITION,
                f"Reposition atomic cannon {cannon_id}",
                {"cannon": cannon_id, "target": target_id},
            )
        )
    return result


def _queue_setup(state: GameState, action: LegalAction) -> list[EngineEvent]:
    cannon_id = str(action.payload["card"])
    target_id = str(action.payload["target"])
    state.players[action.player_id].discard_from_hand(cannon_id)
    state.players[action.player_id].pending_orders.setdefault(
        "atomic_cannon_setup", []
    ).append({"cannon": cannon_id, "target": target_id})
    return [
        EngineEvent(
            "postal_atomic_cannon_setup_ordered",
            action.player_id,
            cannon_id,
            {"target": target_id},
        )
    ]


def _queue_fire(state: GameState, action: LegalAction) -> list[EngineEvent]:
    cannon_id = str(action.payload["cannon"])
    warhead_id = str(action.payload["warhead"])
    state.players[action.player_id].discard_from_hand(warhead_id)
    state.players[action.player_id].pending_orders.setdefault(
        "atomic_cannon", []
    ).append({"cannon": cannon_id, "action": "fire", "warhead_yield": 10})
    return [
        EngineEvent("postal_atomic_cannon_fire_ordered", action.player_id, cannon_id)
    ]


def _queue_reposition(state: GameState, action: LegalAction) -> list[EngineEvent]:
    cannon_id = str(action.payload["cannon"])
    target_id = str(action.payload["target"])
    state.players[action.player_id].pending_orders.setdefault(
        "atomic_cannon", []
    ).append({"cannon": cannon_id, "action": "reposition", "target": target_id})
    return [
        EngineEvent(
            "postal_atomic_cannon_reposition_ordered",
            action.player_id,
            cannon_id,
            {"target": target_id},
        )
    ]


__all__ = ["apply_atomic_action", "atomic_legal_actions"]
