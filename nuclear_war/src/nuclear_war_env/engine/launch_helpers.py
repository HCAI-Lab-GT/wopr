"""Helper utilities for launch resolution."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.final_strike import run_final_strike
from nuclear_war_env.engine.target_policy import opponents_by_population
from nuclear_war_env.integer_validation import positive_int_or_zero
from nuclear_war_env.state import GameState, PlayerState, Ruleset

SUSPENDED_LAUNCH_CLEANUP = "_suspended_launch_cleanup"


def warhead_yield(card: Card) -> int:
    value = card.value if card.value is not None else card.metadata.get("yield", 0)
    return value if type(value) is int else 0


def delivery_capacity(card: Card) -> int:
    max_yield = positive_int_or_zero(card.metadata.get("max_yield_megatons", 0))
    if max_yield > 0 and _is_bomber(card):
        return max_yield
    capacity = card.metadata.get("capacity")
    if capacity is None:
        capacity = card.value if card.value is not None else 1
    return positive_int_or_zero(capacity)


def can_load_warhead(
    state: GameState,
    delivery_id: str,
    launch: dict[str, object],
    warhead: Card,
) -> bool:
    delivery = state.card_by_id(delivery_id)
    warhead_value = warhead_yield(warhead)
    warheads = launch.get("warheads", [])
    if not isinstance(warheads, list):
        return False
    if is_mx_missile(delivery):
        return warhead_value > 10 and not warheads
    max_yield = positive_int_or_zero(delivery.metadata.get("max_yield_megatons", 0))
    if max_yield > 0 and warhead_value > max_yield:
        return False
    if _is_bomber(delivery):
        loaded = sum(warhead_yield(state.card_by_id(card_id)) for card_id in warheads)
        dropped = positive_int_or_zero(launch.get("dropped", 0))
        return loaded + dropped + warhead_value <= delivery_capacity(delivery)
    return len(warheads) < delivery_capacity(delivery)


def attempt_intercept(
    state: GameState,
    target: PlayerState,
    total_yield: int,
    delivery: Card | None = None,
    use_hand: bool = True,
) -> str | None:
    """Intercept an incoming launch with an eligible anti-missile, if any.

    Table mode plays anti-missiles reactively from the target's HAND (V1 policy: always
    intercept when able — the rational play, and the seam for a future agent decision).
    Postal mode pre-orders a defense via its POSTAL_DEFENSE action, held in
    ``pending_orders['defense']``; that queue is honoured first. Only the eligible card
    is consumed; if none is eligible nothing is removed.

    When ``use_hand`` is False the auto hand-scan is skipped and only the defense queue
    is consulted; the decision loop passes ``use_hand=False`` because the defender's
    choice is already queued explicitly (or declined).
    """
    intercept_by = delivery.metadata.get("intercept_by", ()) if delivery else ()
    queue = target.pending_orders.get("defense") or []
    for index, defense_id in enumerate(queue):
        if _intercept_eligible(state, defense_id, intercept_by, total_yield):
            queue.pop(index)
            if defense_id in target.hand:
                # Postal conditional orders keep the card in hand until it
                # actually intercepts; the table decision loop moves the card
                # out of hand when the order is queued, so this is a no-op there.
                target.hand.remove(defense_id)
            return defense_id
    if not use_hand:
        return None
    for card_id in list(target.hand):
        if state.card_by_id(card_id).category is not CardCategory.ANTIMISSILE:
            continue
        if _intercept_eligible(state, card_id, intercept_by, total_yield):
            target.hand.remove(card_id)
            return card_id
    return None


def _intercept_eligible(
    state: GameState,
    card_id: str,
    intercept_by: object,
    total_yield: int,
) -> bool:
    metadata = state.card_by_id(card_id).metadata
    label = metadata.get("label")
    rule = metadata.get("intercept")
    if (
        bool(label)
        and isinstance(intercept_by, (tuple, list, set))
        and label in intercept_by
    ):
        return True
    if rule == "any":
        return True
    return type(rule) is int and total_yield <= rule


def eligible_hand_antimissiles(
    state: GameState,
    target: PlayerState,
    total_yield: int,
    delivery: Card | None = None,
) -> list[str]:
    """Anti-missile card ids in the target's hand eligible to intercept this launch.

    In hand order, using the same eligibility test as attempt_intercept, so the FIRST
    element is exactly the card attempt_intercept(use_hand=True) would auto-play. This
    lets the engine offer interception options whose options[0] reproduces the V1
    always-intercept policy for a pick-first heuristic.
    """
    intercept_by = delivery.metadata.get("intercept_by", ()) if delivery else ()
    eligible: list[str] = []
    for card_id in list(target.hand):
        if state.card_by_id(card_id).category is not CardCategory.ANTIMISSILE:
            continue
        if _intercept_eligible(state, card_id, intercept_by, total_yield):
            eligible.append(card_id)
    return eligible


def schedule_final_retaliation(
    state: GameState,
    player: PlayerState,
    eliminated_by: str | None = None,
    auto_resolve_table: bool = True,
) -> list[EngineEvent]:
    queue_table_decision = state.ruleset is Ruleset.TABLE and not auto_resolve_table
    launches = player.pending_orders.pop("launches", {})
    orders: list[dict[str, object]] = []
    for order in launches.values():
        orders.append(
            {
                "delivery": order["delivery"],
                "warheads": list(order.get("warheads", [])),
                "target": order.get("target"),
            }
        )

    # Rules: combine each acceptable delivery system and warhead card the
    # player possesses. Pool order: hand, face-down queue, deterrent slots,
    # then parked final-strike cards.
    hand_deliveries: list[str] = []
    hand_warheads: list[str] = []
    possessed = (
        list(player.hand)
        + [card_id for card_id in player.face_down_queue if card_id is not None]
        + [card_id for card_id in player.deterrents if card_id is not None]
    )
    for card_id in possessed:
        category = state.card_by_id(card_id).category
        if category is CardCategory.DELIVERY:
            hand_deliveries.append(card_id)
        elif category is CardCategory.WARHEAD:
            hand_warheads.append(card_id)

    hand_warheads.extend(player.final_strike_cards)
    player.final_strike_cards = []

    for delivery_id in hand_deliveries:
        card = state.card_by_id(delivery_id)
        order = _retaliation_order(state, delivery_id, card, hand_warheads)
        if order["warheads"]:
            orders.append(order)

    if queue_table_decision:
        orders = _collapse_delivery_orders(orders)
        orders = [order for order in orders if order.get("warheads")]
    if not orders:
        return []

    for order in orders:
        order["eliminated_by"] = eliminated_by
    player.pending_orders.setdefault("final_strike", []).extend(orders)
    if state.ruleset is Ruleset.TABLE and auto_resolve_table:
        # Table mode has no interactive targeting, so assign targets and fire now.
        # Postal keeps its agent-chosen FINAL_STRIKE_TARGET action flow (untargeted).
        assign_retaliation_targets(state, player.player_id, orders, eliminated_by)
        return run_final_strike(state, player, emit_launch_event=False)
    return []


def suspend_launch_cleanup(
    player: PlayerState,
    delivery_id: str | None,
    warhead_ids: list[str],
) -> None:
    """Defer post-resolution discards until final strikes settle.

    ``delivery_id`` is ``None`` when a bomber persists on the launch track
    (its warheads are still discarded; the delivery is kept and its
    ``launches`` order survives the cleanup)."""
    player.pending_orders.setdefault(SUSPENDED_LAUNCH_CLEANUP, []).append(
        {"delivery": delivery_id, "warheads": list(warhead_ids)}
    )


def complete_suspended_launch_cleanups(state: GameState) -> bool:
    if any(
        player.pending_orders.get("final_strike")
        or _has_active_final_strike_launch(player)
        for player in state.players.values()
    ):
        return False
    completed = False
    for player in state.players.values():
        frames = player.pending_orders.pop(SUSPENDED_LAUNCH_CLEANUP, [])
        if not isinstance(frames, list):
            continue
        for frame in frames:
            if not isinstance(frame, dict):
                continue
            delivery_id = frame.get("delivery")
            if isinstance(delivery_id, str):
                state.discard(state.card_by_id(delivery_id))
                launches = player.pending_orders.get("launches")
                if isinstance(launches, dict):
                    launches.pop(delivery_id, None)
                    if not launches:
                        player.pending_orders.pop("launches", None)
            warhead_ids = frame.get("warheads", [])
            if isinstance(warhead_ids, list):
                for warhead_id in warhead_ids:
                    if isinstance(warhead_id, str):
                        state.discard(state.card_by_id(warhead_id))
            completed = True
    return completed


def drop_unresolvable_final_strike_launches(state: GameState) -> bool:
    removed = False
    for player in state.players.values():
        launches = player.pending_orders.get("launches", {})
        if not isinstance(launches, dict):
            continue
        for delivery_id, order in list(launches.items()):
            if not isinstance(order, dict) or not order.get("_final_strike"):
                continue
            target_id = order.get("target")
            if (
                not order.get("warheads")
                or not isinstance(target_id, str)
                or target_id not in state.players
                or not state.players[target_id].alive
            ):
                launches.pop(delivery_id, None)
                removed = True
        if not launches and "launches" in player.pending_orders:
            player.pending_orders.pop("launches")
    return removed


def _has_active_final_strike_launch(player: PlayerState) -> bool:
    launches = player.pending_orders.get("launches", {})
    if not isinstance(launches, dict):
        return False
    return any(
        isinstance(order, dict)
        and order.get("_final_strike")
        and order.get("warheads")
        and order.get("target")
        for order in launches.values()
    )


def assign_retaliation_targets(
    state: GameState,
    player_id: str,
    orders: list[dict[str, object]],
    eliminated_by: str | None,
) -> None:
    """Point every untargeted retaliation order at a deterministic legal target.

    V1 policy: strike the eliminator first (you retaliate against who killed you);
    otherwise the highest-population living opponent. This is the `select_target`
    seam — a future legal-action targeting choice would replace it.
    """
    target_id = _retaliation_target(state, player_id, eliminated_by)
    if target_id is None:
        return
    for order in orders:
        if order.get("warheads") and not order.get("target"):
            order["target"] = target_id


def _retaliation_target(
    state: GameState,
    player_id: str,
    eliminated_by: str | None,
) -> str | None:
    targets = retaliation_targets_by_policy(state, player_id, eliminated_by)
    return targets[0] if targets else None


def retaliation_targets_by_policy(
    state: GameState,
    player_id: str,
    eliminated_by: str | None,
) -> list[str]:
    targets = opponents_by_population(state, player_id)
    if (
        eliminated_by is not None
        and eliminated_by in targets
        and state.players[eliminated_by].alive
    ):
        remaining = [target for target in targets if target != eliminated_by]
        return [eliminated_by, *remaining]
    return targets


def _retaliation_order(
    state: GameState,
    delivery_id: str,
    card: Card,
    hand_warheads: list[str],
) -> dict[str, object]:
    payload: list[str] = []
    order: dict[str, object] = {
        "delivery": delivery_id,
        "capacity": delivery_capacity(card),
        "warheads": payload,
        "target": None,
    }
    while hand_warheads:
        warhead = state.card_by_id(hand_warheads[0])
        if not can_load_warhead(state, delivery_id, order, warhead):
            break
        payload.append(hand_warheads.pop(0))
    return order


def _collapse_delivery_orders(
    orders: list[dict[str, object]],
) -> list[dict[str, object]]:
    collapsed: dict[str, dict[str, object]] = {}
    for order in orders:
        delivery_id = order.get("delivery")
        if isinstance(delivery_id, str):
            collapsed[delivery_id] = order
    return list(collapsed.values())


def _is_bomber(card: Card) -> bool:
    return "bomber" in card.name.casefold()


def is_mx_missile(card: Card) -> bool:
    return card.metadata.get("postal_effect") == "mx_missile"


__all__ = [
    "warhead_yield",
    "delivery_capacity",
    "can_load_warhead",
    "attempt_intercept",
    "complete_suspended_launch_cleanups",
    "drop_unresolvable_final_strike_launches",
    "eligible_hand_antimissiles",
    "schedule_final_retaliation",
    "assign_retaliation_targets",
    "retaliation_targets_by_policy",
    "suspend_launch_cleanup",
    "is_mx_missile",
]
