"""Legal action helpers shared by simulation, CLI, and environments."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action, dedupe_actions
from .actions_deterrents import apply_deterrent_action
from .actions_final_strike import apply_final_strike_action, final_strike_actions
from .actions_postal import apply_postal_action, postal_legal_actions
from .engine import advance_queue, declare_target, draw_phase, execute_launches
from .engine.draw import set_face_down_cards
from .engine.events import EngineEvent
from .hand_count import draw_count
from .state import HAND_LIMIT, GameState
from .turn_effects import consume_skip_turn, has_skip_turn


def legal_actions(state: GameState, player_id: str, mode: str) -> list[LegalAction]:
    if mode not in {"table", "postal"}:
        raise ValueError(f"Unknown mode: {mode}")
    player = state.players[player_id]
    actions = [build_action(player_id, ActionType.PASS, "Pass")]
    final_strikes = final_strike_actions(state, player_id)
    if final_strikes:
        return dedupe_actions(final_strikes)
    if not player.alive:
        return actions
    if has_skip_turn(player):
        return actions
    if draw_count(player) < HAND_LIMIT and (state.draw_pile or state.discard_pile):
        actions.append(build_action(player_id, ActionType.DRAW, "Draw to hand limit"))
    missing_slots = player.face_down_queue.count(None)
    if missing_slots > 0 and player.hand:
        cards = list(player.hand[:missing_slots])
        actions.append(
            build_action(
                player_id,
                ActionType.ENQUEUE,
                f"Queue {', '.join(cards)}",
                {"cards": cards},
            )
        )
    if any(card_id is not None for card_id in player.face_down_queue):
        actions.append(build_action(player_id, ActionType.ADVANCE, "Advance queue"))
    if mode == "postal":
        actions.extend(postal_legal_actions(state, player_id))
    actions.extend(_target_actions(state, player_id))
    if _has_resolvable_launch(player.pending_orders.get("launches", {})):
        actions.append(build_action(player_id, ActionType.RESOLVE, "Resolve launches"))
    return dedupe_actions(actions)


def apply_action(state: GameState, action: LegalAction) -> list[EngineEvent]:
    player = state.players[action.player_id]
    if action.action_type is ActionType.PASS:
        if consume_skip_turn(player):
            return [EngineEvent("turn_skipped", action.player_id)]
        return [EngineEvent("action_passed", action.player_id)]
    if action.action_type is ActionType.DRAW:
        return draw_phase(state, action.player_id)
    if action.action_type is ActionType.ENQUEUE:
        cards = list(action.payload.get("cards", []))
        set_face_down_cards(player, cards)
        return [EngineEvent("cards_enqueued", action.player_id, None, {"cards": cards})]
    if action.action_type is ActionType.ADVANCE:
        event = advance_queue(state, player)
        return [event] if event is not None else []
    if action.action_type is ActionType.TARGET:
        delivery = str(action.payload["delivery"])
        target = str(action.payload["target"])
        if target not in state.players or not state.players[target].alive:
            return []
        declare_target(state, action.player_id, delivery, target)
        return [
            EngineEvent(
                "target_declared",
                action.player_id,
                delivery,
                {"target": target},
            )
        ]
    if action.action_type is ActionType.RESOLVE:
        return execute_launches(state)
    if action.action_type is ActionType.FINAL_STRIKE_TARGET:
        return apply_final_strike_action(state, action)
    if action.action_type is ActionType.MODIFY_DETERRENT:
        return apply_deterrent_action(state, action)
    if action.action_type in {
        ActionType.POSTAL_PROPAGANDA,
        ActionType.POSTAL_VOTE_PEACE,
        ActionType.POSTAL_SECRET_TARGET,
        ActionType.POSTAL_STEAL_SECRET,
        ActionType.POSTAL_SABOTAGE,
        ActionType.POSTAL_DEFENSE,
        ActionType.POSTAL_CRUISE_LAUNCH,
        ActionType.POSTAL_CRUISE_DROP,
        ActionType.POSTAL_CRUISE_MOVE,
        ActionType.POSTAL_SUBMARINE_LAUNCH,
        ActionType.POSTAL_SUBMARINE_RELOAD,
        ActionType.POSTAL_SUBMARINE_FIRE,
        ActionType.POSTAL_SUBMARINE_RETURN,
        ActionType.POSTAL_SPACE_PLATFORM_LAUNCH,
        ActionType.POSTAL_SPACE_PLATFORM_DROP,
        ActionType.POSTAL_SPACE_SHUTTLE_RELOAD,
        ActionType.POSTAL_SPACE_SHUTTLE_ATTACK,
        ActionType.POSTAL_KILLER_SATELLITE_LAUNCH,
        ActionType.POSTAL_KILLER_SATELLITE_ATTACK,
        ActionType.POSTAL_SUPERVIRUS_START,
        ActionType.POSTAL_SUPERVIRUS_PASS,
        ActionType.POSTAL_ATOMIC_CANNON_SETUP,
        ActionType.POSTAL_ATOMIC_CANNON_FIRE,
        ActionType.POSTAL_ATOMIC_CANNON_REPOSITION,
    }:
        return apply_postal_action(state, action)
    raise ValueError(f"Unknown action type: {action.action_type}")


def _target_actions(state: GameState, player_id: str) -> list[LegalAction]:
    launches = state.players[player_id].pending_orders.get("launches", {})
    result: list[LegalAction] = []
    for delivery_id, launch in launches.items():
        if not launch.get("warheads"):
            continue
        for target_id, target in state.players.items():
            if target_id == player_id or not target.alive:
                continue
            payload = {"delivery": delivery_id, "target": target_id}
            result.append(
                build_action(
                    player_id,
                    ActionType.TARGET,
                    f"Target {target_id}",
                    payload,
                )
            )
    return result


def _has_resolvable_launch(launches: object) -> bool:
    if not isinstance(launches, dict):
        return False
    return any(
        order.get("warheads") and order.get("target") for order in launches.values()
    )


__all__ = ["ActionType", "LegalAction", "legal_actions", "apply_action"]
