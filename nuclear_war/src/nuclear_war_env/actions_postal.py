"""Postal legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .actions_postal_atomic import apply_atomic_action, atomic_legal_actions
from .actions_postal_cruise import apply_cruise_action, cruise_legal_actions
from .actions_postal_defense import apply_defense_action, defense_legal_actions
from .actions_postal_sabotage import apply_sabotage_action, sabotage_legal_actions
from .actions_postal_secret import apply_secret_action, secret_legal_actions
from .actions_postal_space import apply_space_action, space_legal_actions
from .actions_postal_submarine import (
    apply_submarine_action,
    submarine_legal_actions,
)
from .actions_postal_supervirus import (
    apply_supervirus_action,
    supervirus_legal_actions,
)
from .cards import CardCategory
from .engine.events import EngineEvent
from .state import GameState


def postal_legal_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions = secret_legal_actions(state, player_id)
    actions.extend(defense_legal_actions(state, player_id))
    actions.extend(sabotage_legal_actions(state, player_id))
    actions.extend(cruise_legal_actions(state, player_id))
    actions.extend(submarine_legal_actions(state, player_id))
    actions.extend(space_legal_actions(state, player_id))
    actions.extend(supervirus_legal_actions(state, player_id))
    actions.extend(atomic_legal_actions(state, player_id))
    if not state.peace:
        actions.append(
            build_action(player_id, ActionType.POSTAL_VOTE_PEACE, "Vote for peace")
        )
        return actions
    actions.extend(_propaganda_actions(state, player_id))
    return actions


def apply_postal_action(state: GameState, action: LegalAction) -> list[EngineEvent]:
    if action.action_type is ActionType.POSTAL_VOTE_PEACE:
        state.players[action.player_id].pending_orders["vote_peace"] = True
        return [EngineEvent("postal_peace_voted", action.player_id)]
    if action.action_type in {
        ActionType.POSTAL_SECRET_TARGET,
        ActionType.POSTAL_STEAL_SECRET,
    }:
        return apply_secret_action(state, action)
    if action.action_type is ActionType.POSTAL_SABOTAGE:
        return apply_sabotage_action(state, action)
    if action.action_type is ActionType.POSTAL_DEFENSE:
        return apply_defense_action(state, action)
    if action.action_type in {
        ActionType.POSTAL_CRUISE_LAUNCH,
        ActionType.POSTAL_CRUISE_DROP,
        ActionType.POSTAL_CRUISE_MOVE,
    }:
        return apply_cruise_action(state, action)
    if action.action_type in {
        ActionType.POSTAL_SUBMARINE_LAUNCH,
        ActionType.POSTAL_SUBMARINE_RELOAD,
        ActionType.POSTAL_SUBMARINE_FIRE,
        ActionType.POSTAL_SUBMARINE_RETURN,
    }:
        return apply_submarine_action(state, action)
    if action.action_type in {
        ActionType.POSTAL_SPACE_PLATFORM_LAUNCH,
        ActionType.POSTAL_SPACE_PLATFORM_DROP,
        ActionType.POSTAL_SPACE_SHUTTLE_RELOAD,
        ActionType.POSTAL_SPACE_SHUTTLE_ATTACK,
        ActionType.POSTAL_KILLER_SATELLITE_LAUNCH,
        ActionType.POSTAL_KILLER_SATELLITE_ATTACK,
    }:
        return apply_space_action(state, action)
    if action.action_type in {
        ActionType.POSTAL_SUPERVIRUS_START,
        ActionType.POSTAL_SUPERVIRUS_PASS,
    }:
        return apply_supervirus_action(state, action)
    if action.action_type in {
        ActionType.POSTAL_ATOMIC_CANNON_SETUP,
        ActionType.POSTAL_ATOMIC_CANNON_FIRE,
        ActionType.POSTAL_ATOMIC_CANNON_REPOSITION,
    }:
        return apply_atomic_action(state, action)
    if action.action_type is not ActionType.POSTAL_PROPAGANDA:
        return []
    player = state.players[action.player_id]
    card_id = str(action.payload["card"])
    target_id = str(action.payload["target"])
    player.pending_orders.setdefault("propaganda", []).append(card_id)
    player.pending_orders.setdefault("propaganda_orders", {})[card_id] = target_id
    if card_id in player.hand:
        player.discard_from_hand(card_id)
    return [
        EngineEvent(
            "postal_propaganda_ordered",
            action.player_id,
            card_id,
            {"target": target_id},
        )
    ]


def _propaganda_actions(state: GameState, player_id: str) -> list[LegalAction]:
    player = state.players[player_id]
    result: list[LegalAction] = []
    for card_id in player.hand:
        if state.card_by_id(card_id).category is not CardCategory.PROPAGANDA:
            continue
        for target_id, target in state.players.items():
            if target_id == player_id or not target.alive:
                continue
            result.append(
                build_action(
                    player_id,
                    ActionType.POSTAL_PROPAGANDA,
                    f"Propaganda {target_id}",
                    {"card": card_id, "target": target_id},
                )
            )
    return result


__all__ = ["apply_postal_action", "postal_legal_actions"]
