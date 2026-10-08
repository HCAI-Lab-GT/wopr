from copy import deepcopy
from typing import Any

from . import decision_loop as loop
from .action_models import LegalAction
from .agent_names import DECISION_HEURISTIC_AGENT
from .engine.decision import Decision
from .replay import action_to_dict, event_to_dict, final_populations
from .state import GameState
from .variant_catalog import resolve_requested_variant


def legal_action_payload(action: LegalAction) -> dict[str, Any]:
    return {
        "action_id": action.action_id,
        "player_id": action.player_id,
        "action_type": action.action_type.value,
        "label": action.label,
        "payload": deepcopy(action.payload),
    }


def decision_payload(decision: Decision | None, state_version: int) -> dict[str, Any]:
    if decision is None:
        return {"pending": False, "state_version": state_version}
    return {
        "pending": True,
        "state_version": state_version,
        "agent_id": decision.agent_id,
        "decision_type": decision.decision_type.value,
        "context": deepcopy(decision.context),
        "legal_actions": [legal_action_payload(action) for action in decision.options],
    }


def player_payload(state: GameState, player_id: str) -> dict[str, Any]:
    player = state.players[player_id]
    return {
        "player_id": player_id,
        "population": sum(player.population),
        "alive": player.alive,
        "at_war": bool(player.at_war),
        "hand_count": len(player.hand),
        "secret_count": len(player.secrets),
        "deterrent_count": sum(card_id is not None for card_id in player.deterrents),
        "face_up": player.face_up,
        "queue": list(player.face_down_queue),
    }


def state_payload(
    state: GameState,
    *,
    state_version: int,
    source_label: str,
    recent_events: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "state_version": state_version,
        "turn": state.cursor.round if state.cursor is not None else state.turn,
        "source_label": source_label,
        "players": [player_payload(state, player_id) for player_id in state.players],
        "recent_events": deepcopy(recent_events),
        "warnings": [],
    }


def session_payload(
    state: GameState,
    seed: int,
    controlled_players: tuple[str, ...],
    state_version: int,
    complete: bool,
) -> dict[str, Any]:
    controlled = set(controlled_players)
    agent_players = [
        player_id for player_id in state.players if player_id not in controlled
    ]
    return {
        "session_id": f"seed-{seed}-table",
        "mode": "table",
        "seed": seed,
        "players": list(state.players),
        "controlled_players": list(controlled_players),
        "agent_players": agent_players,
        "state_version": state_version,
        "status": "complete" if complete else "running",
    }


def artifacts_payload(
    state: GameState,
    seed: int,
    players: int,
    termination: str | None,
    actions_log: list[dict[str, Any]],
    events_log: list[dict[str, Any]],
) -> dict[str, Any]:
    populations = final_populations(state)
    variant = resolve_requested_variant(state.variant_id, "Live session").to_payload()
    eliminations = [
        player_id for player_id, player in state.players.items() if not player.alive
    ]
    return {
        "replay": {
            "mode": "table",
            "active_variant": variant,
            "seed": seed,
            "agent": DECISION_HEURISTIC_AGENT,
            "players": players,
            "turns": current_turn(state),
            "winner": _winner(termination, populations),
            "termination_reason": termination or "max_turns",
            "final_populations": populations,
            "eliminations": eliminations,
            "pending_final_strikes": any(
                player.pending_orders.get("final_strike")
                for player in state.players.values()
            ),
            "actions": list(actions_log),
            "events": list(events_log),
        },
        "traces": [],
    }


def record_batch(
    actions_log: list[dict[str, Any]],
    events_log: list[dict[str, Any]],
    batch: loop._RoundStamper,
) -> list[dict[str, Any]]:
    actions_log.extend(action_to_dict(action, turn) for action, turn in batch.actions)
    events = [event_to_dict(event, turn) for event, turn in batch.events]
    events_log.extend(events)
    return events


def current_turn(state: GameState) -> int:
    if state.cursor is None:
        return max(1, state.turn)
    if loop.at_round_boundary(state) or loop.pending_decision(state) is None:
        return max(1, state.cursor.round - 1)
    return max(1, state.cursor.round)


def _winner(termination: str | None, populations: dict[str, int]) -> str | None:
    if termination != "one_player_remaining":
        return None
    return next((pid for pid, pop in populations.items() if pop > 0), None)
