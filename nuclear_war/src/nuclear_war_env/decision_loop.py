"""Decision-point state machine driving a faithful table turn."""

from __future__ import annotations

from dataclasses import dataclass, field

from .action_models import ActionType, LegalAction, build_action
from .actions import legal_actions
from .actions_deterrents import apply_deterrent_action, deterrent_actions
from .actions_final_strike import apply_final_strike_action
from .agent_protocol import DecisionAgent
from .cards import CardCategory
from .engine.decision import Decision, DecisionCursor, DecisionType, TurnPhase
from .engine.draw import set_face_down_cards
from .engine.events import EngineEvent
from .engine.final_strike import begin_final_strike_launches, run_final_strike
from .engine.launch import execute_launches
from .engine.launch_helpers import (
    complete_suspended_launch_cleanups,
    drop_unresolvable_final_strike_launches,
    eligible_hand_antimissiles,
    retaliation_targets_by_policy,
    warhead_yield,
)
from .engine.postal.secret_effects import apply_secret_effect
from .engine.propaganda_resolution import _propaganda_value, apply_propaganda_steal
from .engine.secret_resolution import is_self_secret
from .engine.target_policy import opponents_by_population
from .observation import observe
from .state import FACE_DOWN_SLOTS, GameState
from .table_turn import (
    TurnResult,
    _draw_step,
    _placement_order,
    _slide_step,
)
from .variant_catalog import resolve_requested_variant


@dataclass
class _RoundStamper:
    """Pairs each applied action/event with the round it was produced in.

    ``apply_decision_result`` and ``start_game`` can advance through more than one
    player-turn (a player's resolve runs, then the next player's mandatory pre-
    decision steps run before the loop pauses again, possibly in a new round). The
    legacy table runner stamped replay turns by round, so the loop records the
    round for every action/event, letting the runner reproduce the same per-round
    turn numbers regardless of where a round boundary falls inside the batch.
    """

    result: TurnResult
    actions: list[tuple[LegalAction, int]] = field(default_factory=list)
    events: list[tuple[EngineEvent, int]] = field(default_factory=list)
    _action_cursor: int = 0
    _event_cursor: int = 0

    def stamp(self, round_no: int) -> None:
        """Stamp everything appended to ``result`` since the last stamp."""
        while self._action_cursor < len(self.result.actions):
            self.actions.append((self.result.actions[self._action_cursor], round_no))
            self._action_cursor += 1
        while self._event_cursor < len(self.result.events):
            self.events.append((self.result.events[self._event_cursor], round_no))
            self._event_cursor += 1


def start_game(state: GameState, stop_at_round_boundary: bool = False) -> _RoundStamper:
    order = list(state.players)
    # Seed the round with every player (turn_player_ids uses `pending = set(order)`)
    # so the first player is discarded at the first turnover, exactly as the legacy
    # generator discards each player as it yields it. The first player of the game
    # is the clockwise start player (order[0] when no anchor is set yet).
    cursor = DecisionCursor(turn_player=order[0], phase=TurnPhase.DRAW)
    cursor.round_pending = set(order)
    state.cursor = cursor
    state.cursor.turn_player = _pick_round_player(state, order, just_yielded=None)
    if _setup_place_decision(state) is not None:
        # Opening commitment was deferred to the decision loop (a setup created
        # with defer_opening_commitment): surface SETUP_PLACE decisions before
        # the first player's DRAW. Auto-committed states skip this entirely.
        state.cursor.phase = TurnPhase.SETUP
    # The mandatory pre-decision steps the first player takes (draw / slide /
    # propaganda) are real actions+events the replay log must record, so the
    # round-stamped batch is returned to the caller (run_simulation), not discarded.
    stamper = _RoundStamper(TurnResult())
    _advance(state, stamper, stop_at_round_boundary)
    return stamper


def pending_decision(state: GameState) -> Decision | None:
    return None if state.cursor is None else state.cursor.pending


def at_round_boundary(state: GameState) -> bool:
    """True when the loop has paused between rounds (not at a terminal state).

    Only meaningful when the loop is driven with ``stop_at_round_boundary`` and
    ``pending_decision`` is ``None``: it distinguishes "round finished, more game
    to play" from "game over". The runner checks ``max_turns`` here and resumes.
    """
    return (
        state.cursor is not None
        and state.cursor.pending is None
        and _game_continues(state)
    )


def resume_round(
    state: GameState, stop_at_round_boundary: bool = False
) -> _RoundStamper:
    """Run the next round's mandatory steps up to the next decision/boundary."""
    stamper = _RoundStamper(TurnResult())
    _advance(state, stamper, stop_at_round_boundary)
    return stamper


def apply_decision_result(
    state: GameState, action: LegalAction, stop_at_round_boundary: bool = False
) -> _RoundStamper:
    """Apply a decision and auto-advance, returning the round-stamped batch.

    The batch contains the chosen action, the mandatory RESOLVE that an attack
    triggers, and every mandatory step the loop runs while advancing to the next
    decision — exactly the actions/events ``play_table_turn`` produced, so the
    replay log stays identical to the legacy table runner. Each entry is paired
    with the round it occurred in.
    """
    assert state.cursor is not None
    stamper = _RoundStamper(TurnResult())
    result = stamper.result
    if action.action_type is ActionType.SETUP_PLACE:
        # FIDELITY: the opening commitment is applied DIRECTLY (not via apply_action)
        # so it reproduces commit_initial_face_down_cards exactly — no cards_enqueued
        # event, no `_last_placed` bookkeeping, zero RNG. options[0] twice == hand[:2].
        result.actions.append(action)
        card_id = str(action.payload["cards"][0])
        set_face_down_cards(state.players[action.player_id], [card_id])
    elif action.action_type is ActionType.STRATEGY_REPLACE:
        # FIDELITY: the peace-restoration replacement window. A decline (empty
        # payload) closes the player's window; a replacement swaps a hand card
        # into a face-down slot and returns the displaced card to hand (the
        # rules do not say where the old card goes; swap-to-hand is the
        # documented choice). At most two replacements per restoration.
        result.actions.append(action)
        player = state.players[action.player_id]
        if not action.payload:
            player.pending_orders.pop(STRATEGY_REPLACE_REMAINING, None)
        else:
            slot = int(action.payload["slot"])
            new_card = str(action.payload["card"])
            old_card = player.face_down_queue[slot]
            player.face_down_queue[slot] = new_card
            player.hand.remove(new_card)
            if old_card is not None:
                player.hand.append(old_card)
            remaining = int(player.pending_orders.get(STRATEGY_REPLACE_REMAINING, 1))
            if remaining <= 1:
                player.pending_orders.pop(STRATEGY_REPLACE_REMAINING, None)
            else:
                player.pending_orders[STRATEGY_REPLACE_REMAINING] = remaining - 1
    elif action.action_type is ActionType.SECRET_TARGET:
        # PARITY: a SECRET_TARGET decision is applied DIRECTLY (not via apply_action)
        # — the secret was parked out of hand at draw, so it never went through the
        # normal action machinery. Reuse apply_secret_effect so the event stream is
        # byte-identical to resolve_secrets, then drop the resolved secret.
        result.actions.append(action)
        secret_id = str(action.payload["card"])
        target_id = str(action.payload["target"])
        result.events.extend(
            apply_secret_effect(
                state,
                action.player_id,
                secret_id,
                target_id,
                auto_resolve_table=False,
            )
        )
        secrets = state.players[action.player_id].secrets
        if secret_id in secrets:
            secrets.remove(secret_id)
    elif action.action_type is ActionType.PROPAGANDA_TARGET:
        # PARITY: a PROPAGANDA_TARGET decision is applied DIRECTLY (not via
        # apply_action) — the propaganda card was parked during slide, so it never
        # went through the normal action machinery. Reuse apply_propaganda_steal so
        # the event stream is byte-identical to resolve_propaganda, then drop the
        # resolved card so the next pass picks up the following propaganda (if any).
        result.actions.append(action)
        card_id = str(action.payload["card"])
        target_id = str(action.payload["target"])
        result.events.extend(
            apply_propaganda_steal(state, action.player_id, card_id, target_id)
        )
        pending = state.players[action.player_id].pending_orders.get("propaganda", [])
        if card_id in pending:
            pending.remove(card_id)
    elif action.action_type is ActionType.INTERCEPT:
        # PARITY: the defender's choice is applied DIRECTLY. A chosen anti-missile is
        # moved hand -> defense queue so execute_launches consumes it; a decline
        # queues nothing. Then resolve the launch with the hand auto-scan OFF (the
        # decision already happened) — reusing execute_launches keeps the spinner /
        # damage / discard / final-strike event stream byte-identical.
        result.actions.append(action)
        defender = state.players[action.player_id]
        card_id = action.payload.get("card")
        if card_id and card_id in defender.hand:
            defender.hand.remove(card_id)
            defender.pending_orders.setdefault("defense", []).append(card_id)
        pending = state.cursor.pending
        context = pending.context if pending is not None else {}
        result.events.extend(
            execute_launches(
                state,
                emit_launch_event=context.get("emit_launch_event") is not False,
                use_hand_intercept=False,
                auto_resolve_final_strike=False,
                only_attacker_id=_optional_context_str(context, "attacker"),
                only_delivery_id=_optional_context_str(context, "delivery"),
            )
        )
        if context.get("final_strike") is True:
            state.cursor.phase = state.cursor.resume_phase or TurnPhase.ATTACK
        else:
            state.cursor.phase = TurnPhase.ATTACK
    elif action.action_type is ActionType.FINAL_STRIKE_TARGET:
        result.actions.append(action)
        result.events.extend(apply_final_strike_action(state, action))
        result.events.extend(
            begin_final_strike_launches(
                state,
                state.players[action.player_id],
            )
        )
        state.cursor.phase = state.cursor.resume_phase or TurnPhase.ATTACK
    elif action.action_type is ActionType.MODIFY_DETERRENT:
        result.actions.append(action)
        result.events.extend(apply_deterrent_action(state, action))
        state.cursor.phase = TurnPhase.PLACE
    else:
        result.apply(state, action)
        if action.action_type is ActionType.ENQUEUE:
            # PARITY: replicate _place_step's launch-building bookkeeping
            # (table_turn.py:136-141). _placement_order reads `_last_placed` on the
            # player's NEXT turn to prefer a warhead after a delivery; without this
            # the next turn's option ordering — and the agent's options[0] pick —
            # diverges.
            placed = action.payload.get("cards", [None])[0]
            if placed is not None:
                category = state.card_by_id(placed).category
                state.players[action.player_id].pending_orders["_last_placed"] = (
                    "delivery" if category is CardCategory.DELIVERY else "other"
                )
        if action.action_type is ActionType.TARGET:
            # Do NOT auto-resolve. The launch is declared; pause for the
            # defender's INTERCEPT decision before the spinner/damage resolves.
            state.cursor.phase = TurnPhase.INTERCEPT
    state.cursor.pending = None
    _advance(state, stamper, stop_at_round_boundary)
    return stamper


def apply_decision(state: GameState, action: LegalAction) -> list[EngineEvent]:
    return apply_decision_result(state, action).result.events


def _advance(
    state: GameState,
    stamper: _RoundStamper,
    stop_at_round_boundary: bool = False,
) -> None:
    """Advance the loop to the next decision (mutating ``state``).

    With ``stop_at_round_boundary`` the loop also pauses the moment a round
    completes — before the next round's first player takes any mandatory step —
    leaving the cursor at ``(next_player, DRAW)`` with ``pending = None``. The
    simulation runner uses this to check ``max_turns`` termination once per round
    exactly where the legacy outer loop did, so a capped game's state never runs
    into the round past the cap. Callers that want a continuous game (the unit-
    test ``run_decisions`` path) leave it ``False`` and the loop auto-resumes.
    """
    assert state.cursor is not None
    result = stamper.result
    while True:
        if state.cursor.phase is TurnPhase.SETUP:
            setup = _setup_place_decision(state)
            if setup is not None:
                state.cursor.pending = setup
                stamper.stamp(state.cursor.round)
                return
            state.cursor.phase = TurnPhase.DRAW
        if state.peace and not state.cursor.peace_seen:
            # Peace was just restored: "each player may alter their strategy by
            # replacing one or two face down cards with cards from their hand."
            _open_strategy_replacement_window(state)
        state.cursor.peace_seen = state.peace
        replace = _strategy_replace_decision(state)
        if replace is not None:
            state.cursor.pending = replace
            stamper.stamp(state.cursor.round)
            return
        final_strike = _final_strike_decision(state)
        if final_strike is not None:
            _suspend_phase_for_final_strike(state)
            state.cursor.pending = final_strike
            state.cursor.phase = TurnPhase.FINAL_STRIKE
            stamper.stamp(state.cursor.round)
            return
        if _has_pending_final_strike(state):
            _suspend_phase_for_final_strike(state)
        if _run_final_strike_without_decision(state, result):
            stamper.stamp(state.cursor.round)
            continue
        if drop_unresolvable_final_strike_launches(state):
            continue
        _restore_phase_after_final_strike(state)
        intercept = _intercept_decision(state)
        if intercept is not None:
            state.cursor.pending = intercept
            state.cursor.phase = TurnPhase.INTERCEPT
            stamper.stamp(state.cursor.round)
            return
        if complete_suspended_launch_cleanups(state):
            continue
        player_id = state.cursor.turn_player
        player = state.players[player_id]
        # PARITY: a player who is already dead at the START of their turn takes no
        # step at all — the legacy runner `continue`s past them
        # (simulation.run_simulation) and play_table_turn returns immediately for a
        # dead player. Then guard every remaining step on the player still being
        # alive, because a secret's chain reaction can eliminate the drawer mid-turn;
        # once dead they take no further step. Dropping these guards makes a dead
        # player keep drawing/sliding/placing and the outcome diverges.
        if state.cursor.phase is TurnPhase.DRAW:
            if player.alive:
                _draw_step(state, player_id, result)
            state.cursor.phase = TurnPhase.SECRETS
        if state.cursor.phase is TurnPhase.SECRETS:
            if player.alive:
                decision = _secret_decision(state, player_id, result)
                if decision is not None:
                    state.cursor.pending = decision
                    stamper.stamp(state.cursor.round)
                    return
            state.cursor.phase = TurnPhase.SLIDE
        if state.cursor.phase is TurnPhase.SLIDE:
            if player.alive:
                _slide_step(state, player_id, result)
            state.cursor.phase = TurnPhase.PROPAGANDA
        if state.cursor.phase is TurnPhase.PROPAGANDA:
            if player.alive:
                decision = _propaganda_decision(state, player_id)
                if decision is not None:
                    state.cursor.pending = decision
                    stamper.stamp(state.cursor.round)
                    return
            state.cursor.phase = TurnPhase.DETERRENTS
        if state.cursor.phase is TurnPhase.DETERRENTS:
            if player.alive:
                state.cursor.pending = _deterrent_decision(state, player_id)
                stamper.stamp(state.cursor.round)
                return
            state.cursor.phase = TurnPhase.PLACE
        if state.cursor.phase is TurnPhase.PLACE:
            # A player eliminated during the steps above skips PLACE (and ATTACK).
            place = _place_decision(state, player_id) if player.alive else None
            if place is not None:
                state.cursor.pending = place
                stamper.stamp(state.cursor.round)
                return
            state.cursor.phase = TurnPhase.ATTACK
        if state.cursor.phase is TurnPhase.ATTACK:
            target = _launch_target_decision(state, player_id) if player.alive else None
            if target is not None:
                state.cursor.pending = target
                stamper.stamp(state.cursor.round)
                return
            state.cursor.phase = TurnPhase.END
        if state.cursor.phase is TurnPhase.INTERCEPT:
            decision = _intercept_decision(state)
            if decision is not None:
                state.cursor.pending = decision
                stamper.stamp(state.cursor.round)
                return
            state.cursor.phase = TurnPhase.ATTACK
        # END: hand the turn to the next player in the round (or finish).
        # Stamp this player's just-finished turn at the CURRENT round before the
        # turnover, which may advance the round counter for the next player.
        stamper.stamp(state.cursor.round)
        round_before = state.cursor.round
        state.cursor.turn_player = _next_turn_player(state)
        state.cursor.phase = TurnPhase.DRAW
        if state.cursor.round != round_before:
            # A round just completed. PARITY: the legacy runner only checks
            # termination *after* a full round (turn_player_ids yields every
            # still-pending player before the outer loop's _termination_reason
            # call), so a player eliminated mid-round still lets the remaining
            # players in that round act. Terminating now — at the round boundary —
            # when fewer than two survive matches that: no lone survivor loops
            # forever, and no in-round turn is skipped.
            if not _game_continues(state):
                state.cursor.pending = None
                return
            if stop_at_round_boundary:
                # Pause before the new round's first player takes any step so the
                # runner can apply the per-round max_turns check without the next
                # round's state mutations leaking in.
                state.cursor.pending = None
                return


def _suspend_phase_for_final_strike(state: GameState) -> None:
    assert state.cursor is not None
    if (
        state.cursor.resume_phase is None
        and state.cursor.phase is not TurnPhase.FINAL_STRIKE
    ):
        state.cursor.resume_phase = state.cursor.phase


def _restore_phase_after_final_strike(state: GameState) -> None:
    assert state.cursor is not None
    if state.cursor.resume_phase is None or _has_final_strike_activity(state):
        return
    state.cursor.phase = state.cursor.resume_phase
    state.cursor.resume_phase = None


def _has_pending_final_strike(state: GameState) -> bool:
    for player in state.players.values():
        orders = player.pending_orders.get("final_strike")
        if isinstance(orders, list) and orders:
            return True
    return False


def _has_final_strike_activity(state: GameState) -> bool:
    if _has_pending_final_strike(state):
        return True
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


def _setup_place_decision(state: GameState) -> Decision | None:
    """The next opening-commitment decision, or None once every player committed.

    The rules make the two opening face-down cards a strategic commitment
    ("the player is now committed to a specific strategy"), so each empty
    opening slot is an agent decision. Players are visited in seat order and
    options follow hand order, so a pick-first agent reproduces the legacy
    auto-commit of ``hand[:2]`` exactly (engine-orders pattern, zero RNG).
    """
    variant = resolve_requested_variant(state.variant_id, "Setup")
    target = min(variant.initial_face_down_cards, FACE_DOWN_SLOTS)
    for player_id, player in state.players.items():
        committed = sum(1 for card in player.face_down_queue if card is not None)
        if committed >= target or not player.hand:
            continue
        options = [
            build_action(
                player_id,
                ActionType.SETUP_PLACE,
                f"Commit {card_id} face down",
                {"cards": [card_id]},
            )
            for card_id in player.hand
        ]
        return Decision(player_id, DecisionType.SETUP_PLACE, options)
    return None


STRATEGY_REPLACE_REMAINING = "strategy_replace_remaining"


def _open_strategy_replacement_window(state: GameState) -> None:
    """Grant every living player up to two replacements after a restoration."""
    for player in state.players.values():
        if not player.alive:
            continue
        if not player.hand:
            continue
        if not any(card is not None for card in player.face_down_queue):
            continue
        player.pending_orders[STRATEGY_REPLACE_REMAINING] = 2


def _strategy_replace_decision(state: GameState) -> Decision | None:
    """The next open replacement window, seat order; decline is options[0].

    Only face-down queue slots are replaceable (the rules exclude the card
    already turned face up). The decline-first ordering keeps pick-first agents
    on the legacy no-replacement behavior (engine-orders pattern, zero RNG).
    """
    for player_id, player in state.players.items():
        remaining = player.pending_orders.get(STRATEGY_REPLACE_REMAINING)
        if not remaining:
            continue
        slots = [
            index
            for index, card in enumerate(player.face_down_queue)
            if card is not None
        ]
        if not player.alive or not slots or not player.hand:
            player.pending_orders.pop(STRATEGY_REPLACE_REMAINING, None)
            continue
        options = [
            build_action(
                player_id,
                ActionType.STRATEGY_REPLACE,
                "Keep current strategy",
                {},
            )
        ]
        options.extend(
            build_action(
                player_id,
                ActionType.STRATEGY_REPLACE,
                f"Replace face-down slot {slot} with {card_id}",
                {"card": card_id, "slot": slot},
            )
            for slot in slots
            for card_id in player.hand
        )
        return Decision(player_id, DecisionType.STRATEGY_REPLACE, options)
    return None


def _secret_decision(
    state: GameState, player_id: str, result: TurnResult
) -> Decision | None:
    """Auto-resolve self/no-target secrets; return the first offensive SECRET_TARGET.

    Mirrors engine.secret_resolution.resolve_secrets: process secrets in order, halt
    when the drawer dies, gains resolve to the drawer, and an offensive secret with
    no living opponent is a no-op discard. Returns the SECRET_TARGET decision for the
    first offensive secret that has a living opponent, else None when secrets are
    exhausted.
    """
    player = state.players[player_id]
    while player.secrets and player.alive:
        secret_id = player.secrets[0]
        card = state.card_by_id(secret_id)
        if is_self_secret(card):
            result.events.extend(
                apply_secret_effect(state, player_id, secret_id, player_id)
            )
            if secret_id in player.secrets:
                player.secrets.remove(secret_id)
            continue
        targets = opponents_by_population(state, player_id)
        if not targets:
            player.secrets.pop(0)
            continue
        options = [
            build_action(
                player_id,
                ActionType.SECRET_TARGET,
                f"Target secret {secret_id} at {target_id}",
                {"card": secret_id, "target": target_id},
            )
            for target_id in targets
        ]
        return Decision(player_id, DecisionType.SECRET_TARGET, options)
    return None


def _propaganda_decision(state: GameState, player_id: str) -> Decision | None:
    """War: drop all pending propaganda (no decision). Peace: first positive card
    surfaces a PROPAGANDA_TARGET decision (options highest-population first)."""
    player = state.players[player_id]
    if not state.peace:
        player.pending_orders.pop("propaganda", None)
        return None
    pending = player.pending_orders.get("propaganda", [])
    while pending:
        card_id = pending[0]
        if _propaganda_value(state.card_by_id(card_id).metadata) <= 0:
            pending.pop(0)
            continue
        targets = opponents_by_population(state, player_id)
        if not targets:
            pending.pop(0)
            continue
        options = [
            build_action(
                player_id,
                ActionType.PROPAGANDA_TARGET,
                f"Steal {card_id} from {target_id}",
                {"card": card_id, "target": target_id},
            )
            for target_id in targets
        ]
        return Decision(player_id, DecisionType.PROPAGANDA_TARGET, options)
    player.pending_orders.pop("propaganda", None)
    return None


def _place_decision(state: GameState, player_id: str) -> Decision | None:
    player = state.players[player_id]
    cards = _placement_options_order(state, player_id)
    if player.face_down_queue.count(None) <= 0 or not cards:
        return None
    options = [
        build_action(
            player_id, ActionType.ENQUEUE, f"Place {card_id}", {"cards": [card_id]}
        )
        for card_id in cards
    ]
    return Decision(player_id, DecisionType.PLACE, options)


def _placement_options_order(state: GameState, player_id: str) -> list[str]:
    player = state.players[player_id]
    hand_order = _placement_order(state, player_id)
    deterrents = [card_id for card_id in player.deterrents if card_id is not None]
    return hand_order + [card_id for card_id in deterrents if card_id not in hand_order]


def _deterrent_decision(state: GameState, player_id: str) -> Decision:
    return Decision(
        player_id,
        DecisionType.MODIFY_DETERRENT,
        deterrent_actions(state, player_id),
    )


def _launch_target_decision(state: GameState, player_id: str) -> Decision | None:
    options = [
        action
        for action in legal_actions(state, player_id, "table")
        if action.action_type is ActionType.TARGET
    ]
    if not options:
        return None
    options.sort(key=lambda a: sum(state.players[str(a.payload["target"])].population))
    return Decision(player_id, DecisionType.LAUNCH_TARGET, options)


def _intercept_decision(state: GameState) -> Decision | None:
    """Build the defender's INTERCEPT decision for the just-declared launch.

    Always offered (per the rules: the defender signifies non-interception even with
    no anti-missile). Options are the eligible anti-missiles in the defender's hand
    (hand order, so options[0] == attempt_intercept's auto-pick) followed by a single
    decline (empty payload). The total yield matches execute_launches (smart-bomb
    doubling included) so eligibility is identical.
    """
    for attacker_id, attacker in state.players.items():
        launches = attacker.pending_orders.get("launches", {})
        if not isinstance(launches, dict):
            continue
        for delivery_id, order in launches.items():
            target_id = order.get("target")
            if (
                not order.get("warheads")
                or not isinstance(target_id, str)
                or target_id not in state.players
                or not state.players[target_id].alive
            ):
                continue
            target = state.players[target_id]
            delivery = state.card_by_id(delivery_id)
            total_yield = sum(
                warhead_yield(state.card_by_id(w)) for w in order["warheads"]
            )
            if order.get("smart_bomb") and total_yield in {10, 20}:
                total_yield *= 2
            options = [
                build_action(
                    target_id,
                    ActionType.INTERCEPT,
                    f"Intercept {delivery_id} with {am}",
                    {"card": am},
                )
                for am in eligible_hand_antimissiles(
                    state, target, total_yield, delivery
                )
            ]
            options.append(
                build_action(
                    target_id, ActionType.INTERCEPT, "Decline interception", {}
                )
            )
            return Decision(
                target_id,
                DecisionType.INTERCEPT,
                options,
                context={
                    "attacker": attacker_id,
                    "delivery": delivery_id,
                    "emit_launch_event": not order.get("_final_strike"),
                    "final_strike": bool(order.get("_final_strike")),
                    "yield": total_yield,
                },
            )
    return None


def _final_strike_decision(state: GameState) -> Decision | None:
    for player_id, player in state.players.items():
        if "final_strike" not in player.pending_orders:
            continue
        orders = player.pending_orders.get("final_strike", [])
        if not isinstance(orders, list):
            continue
        if not orders:
            player.pending_orders.pop("final_strike", None)
            continue
        untargeted = [
            order
            for order in orders
            if isinstance(order, dict)
            and "delivery" in order
            and order.get("warheads")
            and not order.get("target")
        ]
        if not untargeted:
            continue
        eliminated_by = untargeted[0].get("eliminated_by")
        targets = retaliation_targets_by_policy(
            state,
            player_id,
            str(eliminated_by) if eliminated_by is not None else None,
        )
        if not targets:
            return None
        return Decision(
            player_id,
            DecisionType.FINAL_STRIKE_TARGET,
            [
                build_action(
                    player_id,
                    ActionType.FINAL_STRIKE_TARGET,
                    f"Target final strike at {target_id}",
                    {"target": target_id},
                )
                for target_id in targets
            ],
            context={"eliminated_by": eliminated_by},
        )
    return None


def _run_final_strike_without_decision(state: GameState, result: TurnResult) -> bool:
    for player_id, player in state.players.items():
        if "final_strike" not in player.pending_orders:
            continue
        orders = player.pending_orders.get("final_strike", [])
        if not isinstance(orders, list):
            continue
        if not orders:
            player.pending_orders.pop("final_strike", None)
            continue
        untargeted = [
            order
            for order in orders
            if isinstance(order, dict)
            and "delivery" in order
            and order.get("warheads")
            and not order.get("target")
        ]
        if not untargeted:
            if _has_live_targeted_final_strike(state, orders):
                result.events.extend(begin_final_strike_launches(state, player))
            else:
                result.events.extend(
                    run_final_strike(
                        state,
                        player,
                        emit_launch_event=False,
                        auto_resolve_final_strike=False,
                    )
                )
            return True
        eliminated_by = untargeted[0].get("eliminated_by")
        targets = retaliation_targets_by_policy(
            state,
            player_id,
            str(eliminated_by) if eliminated_by is not None else None,
        )
        if targets:
            continue
        result.events.extend(
            run_final_strike(
                state,
                player,
                emit_launch_event=False,
                auto_resolve_final_strike=False,
            )
        )
        return True
    return False


def _has_live_targeted_final_strike(
    state: GameState,
    orders: list[object],
) -> bool:
    for order in orders:
        if not isinstance(order, dict) or "delivery" not in order:
            continue
        target_id = order.get("target")
        if isinstance(target_id, str) and state.players.get(target_id, None):
            if state.players[target_id].alive:
                return True
    return False


def _optional_context_str(context: dict[str, object], key: str) -> str | None:
    value = context.get(key)
    return value if isinstance(value, str) else None


def _game_continues(state: GameState) -> bool:
    return sum(1 for p in state.players.values() if p.alive) >= 2


def _next_turn_player(state: GameState) -> str:
    """Advance one player-turn, reproducing ``turn_player_ids`` exactly.

    ``turn_player_ids`` yields each player once per round (clockwise, honoring an
    interception override while the interceptor is still pending), then advances
    the inter-round anchor to the player after the last one to act. This single-
    step port keeps the same ``round_pending`` set on the cursor and the same
    ``state.current_player_id`` anchor so the loop produces an identical living-
    player turn sequence. Dead players are still "yielded" here (mirroring the
    legacy ``pending = set(order)``) and skipped inside ``_advance``.
    """
    assert state.cursor is not None
    order = list(state.players)
    just_yielded = state.cursor.turn_player
    # Discard the player who just took their turn, matching pending.discard(nxt).
    state.cursor.round_pending.discard(just_yielded)
    if not state.cursor.round_pending:
        # Round complete: set the next-round anchor to the player after the last
        # to act, then reseed the round with every player (turn_player_ids re-runs
        # with a fresh `pending = set(order)` each round) and advance the round
        # counter so subsequent actions are stamped with the new round number.
        state.current_player_id = order[(order.index(just_yielded) + 1) % len(order)]
        state.cursor.round_pending = set(order)
        state.cursor.round += 1
        return _pick_round_player(state, order, just_yielded=None)
    return _pick_round_player(state, order, just_yielded=just_yielded)


def _pick_round_player(
    state: GameState, order: list[str], just_yielded: str | None
) -> str:
    """Port of simulation_turns._next_player against the cursor's round_pending."""
    assert state.cursor is not None
    pending = state.cursor.round_pending
    override = state.next_player_id
    state.next_player_id = None
    if override in pending:
        assert override is not None
        return override
    if just_yielded is None:
        anchor = _start_player(state, order)
        if anchor in pending:
            return anchor
        return _clockwise_pending(order, anchor, pending) or just_yielded or order[0]
    return _clockwise_pending(order, just_yielded, pending) or just_yielded


def _start_player(state: GameState, order: list[str]) -> str:
    current = state.current_player_id
    if current is not None and current in order:
        return current
    return order[0]


def _clockwise_pending(order: list[str], start: str, pending: set[str]) -> str | None:
    size = len(order)
    start_index = order.index(start)
    for step in range(1, size + 1):
        candidate = order[(start_index + step) % size]
        if candidate in pending:
            return candidate
    return None


def run_decisions(
    state: GameState,
    agents: dict[str, DecisionAgent],
    max_turns: int = 200,
) -> None:
    turns = 0
    while (decision := pending_decision(state)) is not None and turns < max_turns:
        agent = agents[decision.agent_id]
        action = agent.choose(observe(state, decision.agent_id), decision.options)
        apply_decision(state, action)
        if state.cursor is not None and state.cursor.phase is TurnPhase.DRAW:
            turns += 1


__all__ = [
    "start_game",
    "pending_decision",
    "at_round_boundary",
    "resume_round",
    "apply_decision",
    "apply_decision_result",
    "run_decisions",
]
