"""Faithful table-mode turn driver.

A real Nuclear War turn is an ordered sequence, not a single action:

1. Draw until the hand reaches the draw target (resolving secrets).
2. Slide the launch track: the first face-down card becomes face-up and resolves.
3. Place one card from hand into the now-empty second face-down slot.
4. Resolve any launch that is ready (a warhead loaded onto a delivery): an attack
   is mandatory, so the player picks a target and fires.

The engine performs the mandatory steps itself and consults ``agent`` only at the
genuine decision points (which card to place, which target to hit). This keeps the
shared ``legal_actions`` / ``apply_action`` vocabulary (so the PettingZoo env and
the simulation share one engine) while making the *sequence* rules-faithful.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .action_models import ActionType, LegalAction, build_action
from .actions import apply_action, legal_actions
from .agent_action_validation import require_legal_agent_action
from .cards import CardCategory
from .engine.events import EngineEvent
from .engine.propaganda_resolution import resolve_propaganda
from .engine.secret_resolution import resolve_secrets
from .hand_count import draw_count
from .state import HAND_LIMIT, GameState


class TurnAgent(Protocol):
    def choose(self, actions: list[LegalAction]) -> LegalAction: ...


def _choose(agent: TurnAgent, options: list[LegalAction]) -> LegalAction:
    """Ask the agent to choose and reject any action outside the offered set."""
    return require_legal_agent_action(agent.choose(options), options)


@dataclass
class TurnResult:
    """The actions taken and events produced during one full table turn.

    Both are surfaced so callers (the simulation runner, replay logs) can record
    the ordered actions a player took, not just the resulting events.
    """

    actions: list[LegalAction] = field(default_factory=list)
    events: list[EngineEvent] = field(default_factory=list)

    def apply(self, state: GameState, action: LegalAction) -> None:
        self.actions.append(action)
        self.events.extend(apply_action(state, action))


def play_table_turn(
    state: GameState,
    player_id: str,
    agent: TurnAgent,
) -> TurnResult:
    """Run one player's full, rules-ordered table turn."""
    result = TurnResult()
    player = state.players[player_id]
    if not player.alive:
        return result
    # A player can be eliminated mid-turn by a chain reaction their own play sets
    # off (a secret's target retaliating, etc.); once dead they take no further step.
    _draw_step(state, player_id, result)
    if player.alive:
        _resolve_secrets_step(state, player_id, result)
    if player.alive:
        _slide_step(state, player_id, result)
    if player.alive:
        _resolve_propaganda_step(state, player_id, result)
    if player.alive:
        _place_step(state, player_id, agent, result)
    if player.alive:
        _attack_step(state, player_id, agent, result)
    return result


def _draw_step(state: GameState, player_id: str, result: TurnResult) -> None:
    player = state.players[player_id]
    if draw_count(player) >= HAND_LIMIT:
        return
    if not state.draw_pile and not state.discard_pile:
        return
    result.apply(state, build_action(player_id, ActionType.DRAW, "Draw"))


def _resolve_secrets_step(state: GameState, player_id: str, result: TurnResult) -> None:
    # Secrets drawn this turn were parked out of hand by the draw step; the rules
    # resolve them the moment they are drawn. Engine-mandatory, so no agent action.
    result.events.extend(resolve_secrets(state, player_id))


def _slide_step(state: GameState, player_id: str, result: TurnResult) -> None:
    player = state.players[player_id]
    if not any(card_id is not None for card_id in player.face_down_queue):
        return
    result.apply(state, build_action(player_id, ActionType.ADVANCE, "Advance"))


def _resolve_propaganda_step(
    state: GameState, player_id: str, result: TurnResult
) -> None:
    # A propaganda card revealed by the slide steals during peace (engine-mandatory,
    # so no agent action); it is inert during war.
    result.events.extend(resolve_propaganda(state, player_id))


def _place_step(
    state: GameState,
    player_id: str,
    agent: TurnAgent,
    result: TurnResult,
) -> None:
    player = state.players[player_id]
    if player.face_down_queue.count(None) <= 0 or not player.hand:
        return
    # Offer one single-card placement per hand card, ordered to build launches; the
    # agent picks which (a pick-first heuristic gets the smart choice, random does not).
    options = [
        build_action(
            player_id,
            ActionType.ENQUEUE,
            f"Place {card_id}",
            {"cards": [card_id]},
        )
        for card_id in _placement_order(state, player_id)
    ]
    chosen = _choose(agent, options)
    result.apply(state, chosen)
    placed = chosen.payload.get("cards", [None])[0]
    if placed is not None:
        category = state.card_by_id(placed).category
        player.pending_orders["_last_placed"] = (
            "delivery" if category is CardCategory.DELIVERY else "other"
        )


def _placement_order(state: GameState, player_id: str) -> list[str]:
    """Order the hand to build delivery->warhead launches.

    A delivery placed one turn and a warhead the next become face-up on consecutive
    turns, so the warhead arms the delivery. After placing a delivery the policy
    prefers a warhead; otherwise it starts a new launch with a delivery.
    """
    player = state.players[player_id]
    deliveries: list[str] = []
    warheads: list[str] = []
    others: list[str] = []
    for card_id in player.hand:
        category = state.card_by_id(card_id).category
        if category is CardCategory.DELIVERY:
            deliveries.append(card_id)
        elif category is CardCategory.WARHEAD:
            warheads.append(card_id)
        else:
            others.append(card_id)
    if player.pending_orders.get("_last_placed") == "delivery" and warheads:
        return warheads + deliveries + others
    if deliveries:
        return deliveries + warheads + others
    if warheads:
        return warheads + others
    return list(player.hand)


def _attack_step(
    state: GameState,
    player_id: str,
    agent: TurnAgent,
    result: TurnResult,
) -> None:
    targets = [
        action
        for action in legal_actions(state, player_id, "table")
        if action.action_type is ActionType.TARGET
    ]
    if targets:
        # Prefer finishing off the weakest opponent (lowest population first).
        targets.sort(
            key=lambda action: sum(
                state.players[str(action.payload["target"])].population
            )
        )
        result.apply(state, _choose(agent, targets))
    resolves = [
        action
        for action in legal_actions(state, player_id, "table")
        if action.action_type is ActionType.RESOLVE
    ]
    if resolves:
        result.apply(state, resolves[0])


__all__ = ["play_table_turn", "TurnResult", "TurnAgent"]
