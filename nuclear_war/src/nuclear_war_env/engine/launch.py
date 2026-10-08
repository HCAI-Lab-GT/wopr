"""Launch resolution integrating fallout and final retaliation."""

from __future__ import annotations

from nuclear_war_env.fallout import SpinnerEffect, spin_spinner
from nuclear_war_env.state import GameState, Ruleset

from .events import EngineEvent
from .launch_helpers import (
    _is_bomber,
    attempt_intercept,
    delivery_capacity,
    is_mx_missile,
    suspend_launch_cleanup,
    warhead_yield,
)
from .launch_resolution import resolve_unblocked_launch, trigger_global_loss
from .mx_missile import resolve_mx_launch
from .spinner_events import spinner_result_event
from .war_state import (
    declare_war_for_launch,
    restore_peace_after_completed_eliminations,
)


def declare_target(
    state: GameState,
    player_id: str,
    delivery_id: str,
    target_id: str,
) -> None:
    launches = state.players[player_id].pending_orders.setdefault("launches", {})
    if delivery_id not in launches:
        raise KeyError(f"No active delivery {delivery_id}")
    if target_id not in state.players:
        raise KeyError(f"Unknown target {target_id}")
    launches[delivery_id]["target"] = target_id
    declare_war_for_launch(state, launches[delivery_id])


def execute_launches(
    state: GameState,
    emit_launch_event: bool = True,
    use_hand_intercept: bool = True,
    auto_resolve_final_strike: bool = True,
    only_attacker_id: str | None = None,
    only_delivery_id: str | None = None,
) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    if only_attacker_id is not None:
        _clear_dead_launch_targets_before(state, only_attacker_id)
    for attacker_id, attacker in state.players.items():
        if only_attacker_id is not None and attacker_id != only_attacker_id:
            continue
        launches = attacker.pending_orders.get("launches", {})
        to_remove: list[str] = []
        for delivery_id, order in list(launches.items()):
            if only_delivery_id is not None and delivery_id != only_delivery_id:
                continue
            target_id = order.get("target")
            if not order["warheads"] or target_id is None:
                continue
            if target_id not in state.players or not state.players[target_id].alive:
                order["target"] = None
                continue
            target = state.players[target_id]
            delivery_card = state.card_by_id(delivery_id)
            warhead_cards = [state.card_by_id(w_id) for w_id in order["warheads"]]
            total_yield = sum(warhead_yield(card) for card in warhead_cards)
            payload_yield = total_yield
            if total_yield <= 0:
                continue
            bomber_spent = True
            declare_war_for_launch(state, order)
            if order.get("smart_bomb") and total_yield in {10, 20}:
                total_yield *= 2
            if emit_launch_event:
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
            pending_final_strikes = _pending_final_strike_count(state)
            defense_id = attempt_intercept(
                state, target, total_yield, delivery_card, use_hand=use_hand_intercept
            )
            if defense_id is not None:
                state.next_player_id = target_id
                events.append(
                    EngineEvent(
                        "intercept_success",
                        target_id,
                        defense_id,
                        {"stopped_delivery": delivery_id},
                    )
                )
                state.discard(state.card_by_id(defense_id))
            elif is_mx_missile(delivery_card):
                events.extend(
                    resolve_mx_launch(
                        state,
                        attacker_id,
                        target_id,
                        delivery_id,
                        order,
                        total_yield,
                        auto_resolve_final_strike=auto_resolve_final_strike,
                    )
                )
            else:
                roll, outcome = spin_spinner(state.rng)
                events.append(spinner_result_event(attacker_id, None, roll, outcome))
                max_single_yield = max(
                    (warhead_yield(card) for card in warhead_cards), default=0
                )
                if (
                    outcome.effect is SpinnerEffect.STOCKPILE_EXPLODES
                    and max_single_yield >= 100
                ):
                    events.extend(trigger_global_loss(state, attacker_id, target_id))
                else:
                    # The 00-04 band is "bomber runs out of fuel" for a bomber;
                    # any other resolved outcome leaves the bomber flying.
                    bomber_spent = outcome.attacker_backfire
                    events.extend(
                        resolve_unblocked_launch(
                            state,
                            attacker_id,
                            target_id,
                            delivery_id,
                            order,
                            total_yield,
                            outcome,
                            auto_resolve_final_strike=auto_resolve_final_strike,
                        )
                    )
            # Rules: a bomber attacks in multiple successive turns until it has
            # dropped warheads equal to its payload (the non-warhead / over-limit
            # window close lives in draw._expire_pending_delivery). It is spent
            # by an intercept, running out of fuel, or exhausting its payload.
            dropped_total = _order_dropped(order) + payload_yield
            bomber_continues = (
                _is_bomber(delivery_card)
                and not order.get("_final_strike")
                and not bomber_spent
                and attacker.alive
                and dropped_total < delivery_capacity(delivery_card)
            )
            if (
                not auto_resolve_final_strike
                and _pending_final_strike_count(state) > pending_final_strikes
            ):
                suspend_launch_cleanup(
                    attacker,
                    None if bomber_continues else delivery_id,
                    [card.identifier for card in warhead_cards],
                )
            else:
                if not bomber_continues:
                    state.discard(delivery_card)
                for warhead in warhead_cards:
                    state.discard(warhead)
                if not bomber_continues:
                    to_remove.append(delivery_id)
            if bomber_continues:
                order["warheads"] = []
                order["target"] = None
                order["dropped"] = dropped_total
            if not attacker.alive:
                # A booster self-kill folds the attacker's remaining launches into
                # final retaliation; stop iterating the snapshot so those absorbed
                # launches are not resolved a second time here.
                break
        for delivery_id in to_remove:
            launches.pop(delivery_id, None)
        if not launches and "launches" in attacker.pending_orders:
            attacker.pending_orders.pop("launches")
    if (
        state.ruleset is Ruleset.TABLE
        and not _has_active_final_strike_launch(state)
        and restore_peace_after_completed_eliminations(state)
    ):
        events.append(EngineEvent("peace_restored", None))
    return events


def _order_dropped(order: dict[str, object]) -> int:
    value = order.get("dropped", 0)
    return value if type(value) is int and value > 0 else 0


def _clear_dead_launch_targets_before(state: GameState, attacker_id: str) -> None:
    for player_id, player in state.players.items():
        if player_id == attacker_id:
            return
        launches = player.pending_orders.get("launches", {})
        if not isinstance(launches, dict):
            continue
        for order in launches.values():
            if not isinstance(order, dict) or not order.get("warheads"):
                continue
            target_id = order.get("target")
            if target_id is None:
                continue
            if target_id not in state.players or not state.players[target_id].alive:
                order["target"] = None


def _has_active_final_strike_launch(state: GameState) -> bool:
    for player in state.players.values():
        launches = player.pending_orders.get("launches", {})
        if not isinstance(launches, dict):
            continue
        if any(
            isinstance(order, dict) and order.get("_final_strike")
            for order in launches.values()
        ):
            return True
    return False


def _pending_final_strike_count(state: GameState) -> int:
    return sum(
        len(orders)
        for player in state.players.values()
        for orders in [player.pending_orders.get("final_strike", [])]
        if isinstance(orders, list)
    )


__all__ = ["declare_target", "execute_launches"]
