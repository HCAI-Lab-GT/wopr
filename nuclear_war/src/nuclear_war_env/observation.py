"""Player-scoped observations for deterministic Nuclear War state."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from .action_models import LegalAction
from .engine.decision import Decision, DecisionType
from .state import GameState, PlayerState


@dataclass(frozen=True)
class PrivatePlayerObservation:
    population: int
    hand: list[str]
    secrets: list[str]
    deterrents: list[str | None]
    face_up: str | None
    face_down_queue: list[str | None]
    final_strike_cards: list[str]
    pending_orders: dict[str, Any]
    alive: bool
    at_war: bool


@dataclass(frozen=True)
class PublicPlayerObservation:
    population: int
    hand_count: int
    secret_count: int
    deterrent_count: int
    face_up: str | None
    face_down_count: int
    alive: bool
    at_war: bool


@dataclass(frozen=True)
class DecisionObservation:
    agent_id: str
    decision_type: DecisionType
    options: list[LegalAction]
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Observation:
    player_id: str
    ruleset: str
    turn: int
    peace: bool
    self: PrivatePlayerObservation
    players: dict[str, PublicPlayerObservation]
    draw_count: int
    discard_count: int
    decision: DecisionObservation | None = None


def observe(state: GameState, player_id: str) -> Observation:
    player = state.players[player_id]
    return Observation(
        player_id=player_id,
        ruleset=state.ruleset.value,
        turn=_observation_turn(state),
        peace=state.peace,
        self=_private_player_observation(player),
        players={
            other_id: _public_player_observation(other)
            for other_id, other in state.players.items()
            if other_id != player_id
        },
        draw_count=len(state.draw_pile),
        discard_count=len(state.discard_pile),
        decision=_decision_observation(state, player_id),
    )


def to_player_observation(state: GameState, player_id: str) -> dict[str, Any]:
    player = state.players[player_id]
    return {
        "player_id": player_id,
        "ruleset": state.ruleset.value,
        "turn": _observation_turn(state),
        "peace": state.peace,
        "self": _private_player(player),
        "players": {
            other_id: _public_player(other)
            for other_id, other in state.players.items()
            if other_id != player_id
        },
        "draw_count": len(state.draw_pile),
        "discard_count": len(state.discard_pile),
    }


def to_numeric_observation(state: GameState, player_id: str) -> list[float]:
    player = state.players[player_id]
    opponents = [other for key, other in state.players.items() if key != player_id]
    return [
        float(_observation_turn(state)),
        float(sum(player.population)),
        float(len(player.hand)),
        float(len(player.secrets)),
        float(sum(1 for card_id in player.face_down_queue if card_id is not None)),
        float(sum(1 for opponent in opponents if opponent.alive)),
    ]


def _private_player_observation(player: PlayerState) -> PrivatePlayerObservation:
    return PrivatePlayerObservation(
        population=sum(player.population),
        hand=list(player.hand),
        secrets=list(player.secrets),
        deterrents=list(player.deterrents),
        face_up=player.face_up,
        face_down_queue=list(player.face_down_queue),
        final_strike_cards=list(player.final_strike_cards),
        pending_orders=deepcopy(player.pending_orders),
        alive=player.alive,
        at_war=player.at_war,
    )


def _observation_turn(state: GameState) -> int:
    return state.cursor.round if state.cursor is not None else state.turn


def _public_player_observation(player: PlayerState) -> PublicPlayerObservation:
    return PublicPlayerObservation(
        population=sum(player.population),
        hand_count=len(player.hand),
        secret_count=len(player.secrets),
        deterrent_count=sum(1 for card_id in player.deterrents if card_id is not None),
        face_up=player.face_up,
        face_down_count=sum(
            1 for card_id in player.face_down_queue if card_id is not None
        ),
        alive=player.alive,
        at_war=player.at_war,
    )


def _decision_observation(
    state: GameState, player_id: str
) -> DecisionObservation | None:
    pending = None if state.cursor is None else state.cursor.pending
    if pending is None or pending.agent_id != player_id:
        return None
    return _copy_decision(pending)


def _copy_decision(decision: Decision) -> DecisionObservation:
    return DecisionObservation(
        agent_id=decision.agent_id,
        decision_type=decision.decision_type,
        options=deepcopy(decision.options),
        context=deepcopy(decision.context),
    )


def _private_player(player: PlayerState) -> dict[str, Any]:
    return {
        "population": sum(player.population),
        "hand": list(player.hand),
        "secrets": list(player.secrets),
        "deterrents": list(player.deterrents),
        "face_up": player.face_up,
        "face_down_queue": list(player.face_down_queue),
        "final_strike_cards": list(player.final_strike_cards),
        "pending_orders": deepcopy(player.pending_orders),
        "alive": player.alive,
        "at_war": player.at_war,
    }


def _public_player(player: PlayerState) -> dict[str, Any]:
    return {
        "population": sum(player.population),
        "hand_count": len(player.hand),
        "secret_count": len(player.secrets),
        "deterrent_count": sum(
            1 for card_id in player.deterrents if card_id is not None
        ),
        "face_up": player.face_up,
        "face_down_count": sum(
            1 for card_id in player.face_down_queue if card_id is not None
        ),
        "alive": player.alive,
        "at_war": player.at_war,
    }


__all__ = [
    "DecisionObservation",
    "Observation",
    "PrivatePlayerObservation",
    "PublicPlayerObservation",
    "observe",
    "to_player_observation",
    "to_numeric_observation",
]
