"""Launch-related postal handlers."""

from __future__ import annotations

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.launch import declare_target, execute_launches
from nuclear_war_env.engine.launch_helpers import attempt_intercept, warhead_yield
from nuclear_war_env.engine.war_state import declare_war_for_launch
from nuclear_war_env.state import GameState

from .sabotage import apply_sabotage_orders


def phase_declare_targets(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        targets = player.pending_orders.pop("targets", {})
        for delivery_id, target_id in targets.items():
            try:
                declare_target(state, player.player_id, delivery_id, target_id)
            except KeyError:
                continue
            events.append(
                EngineEvent(
                    "target_declared",
                    player.player_id,
                    delivery_id,
                    {"target": target_id},
                )
            )
    return events


def phase_sabotage(state: GameState) -> list[EngineEvent]:
    return apply_sabotage_orders(state)


def phase_launch(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for attacker_id, attacker in state.players.items():
        launches = attacker.pending_orders.get("launches", {})
        for delivery_id, order in launches.items():
            target_id = order.get("target")
            if not order["warheads"] or target_id not in state.players:
                continue
            declare_war_for_launch(state, order)
            total_yield = sum(
                warhead_yield(state.card_by_id(w)) for w in order["warheads"]
            )
            events.append(
                EngineEvent(
                    "launch_declared",
                    attacker_id,
                    delivery_id,
                    {
                        "target": target_id,
                        "warheads": list(order["warheads"]),
                        "yield": total_yield,
                    },
                )
            )
    return events


def phase_intercept(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for defender in state.players.values():
        if not defender.alive:
            # A country eliminated earlier this turn (secrets, final strike)
            # cannot execute its conditional defense orders; the launch aimed
            # at it is skipped at nuking, so intercepting would only destroy
            # the attacker's cards.
            defender.pending_orders.pop("defense", None)
            continue
        defenses = defender.pending_orders.get("defense")
        if not defenses:
            continue
        for _defense_id in list(defenses):
            incoming = _find_incoming_launch(state, defender.player_id)
            if not incoming:
                break
            attacker_id, delivery_id, spec = incoming
            delivery_card = state.card_by_id(delivery_id)
            total_yield = sum(
                warhead_yield(state.card_by_id(w)) for w in spec["warheads"]
            )
            stopped_by = attempt_intercept(
                state,
                defender,
                total_yield,
                delivery_card,
                use_hand=False,
            )
            if stopped_by is None:
                continue
            launches = state.players[attacker_id].pending_orders.get("launches", {})
            launch_spec = launches.pop(delivery_id, None)
            if launch_spec is None:
                continue
            for warhead_id in launch_spec["warheads"]:
                state.discard(state.card_by_id(warhead_id))
            state.discard(state.card_by_id(delivery_id))
            state.discard(state.card_by_id(stopped_by))
            events.append(
                EngineEvent(
                    "intercept_success",
                    defender.player_id,
                    stopped_by,
                    {"stopped_delivery": delivery_id},
                )
            )
        if not defender.pending_orders.get("defense"):
            defender.pending_orders.pop("defense", None)
    return events


def phase_nuking(state: GameState) -> list[EngineEvent]:
    # Postal interception is driven by conditional defense orders (consumed via
    # the pending "defense" queue); the table-mode hand auto-scan stays off.
    events = execute_launches(state, emit_launch_event=False, use_hand_intercept=False)
    for player in state.players.values():
        # Unused conditional orders expire once the turn's launches resolved;
        # the committed cards stay in hand for a future order.
        player.pending_orders.pop("defense", None)
    return events


def _find_incoming_launch(
    state: GameState,
    defender_id: str,
) -> tuple[str, str, dict] | None:
    for attacker_id, attacker in state.players.items():
        launches = attacker.pending_orders.get("launches", {})
        for delivery_id, spec in launches.items():
            if spec.get("target") == defender_id and spec.get("warheads"):
                return attacker_id, delivery_id, spec
    return None


__all__ = [
    "phase_declare_targets",
    "phase_sabotage",
    "phase_launch",
    "phase_intercept",
    "phase_nuking",
]
