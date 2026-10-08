"""Supervirus handling for postal play."""

from __future__ import annotations

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.fallout import roll_nuke_die
from nuclear_war_env.population import remove_population_with_bank
from nuclear_war_env.state import GameState, PlayerState


def apply_supervirus_orders(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    started: set[str] = set()
    for player in state.players.values():
        if not player.alive:
            continue
        order = player.pending_orders.pop("supervirus_start", None)
        if not isinstance(order, dict):
            continue
        target_id = str(order.get("target", ""))
        card_id = str(order.get("card", ""))
        if (
            target_id not in state.players
            or not state.players[target_id].alive
            or not card_id
            or _is_immune(state, target_id)
        ):
            continue
        loss = _infect(state, target_id, card_id, player.player_id)
        started.add(target_id)
        events.append(
            EngineEvent(
                "supervirus_started",
                player.player_id,
                card_id,
                {"target": target_id, "loss": loss},
            )
        )
    for holder in state.players.values():
        if holder.player_id in started:
            continue
        infection = holder.pending_orders.get("supervirus")
        order = holder.pending_orders.pop("supervirus_pass", None)
        if not isinstance(infection, dict):
            continue
        card_id = str(infection.get("card", ""))
        if not holder.alive:
            holder.pending_orders.pop("supervirus", None)
            events.append(
                EngineEvent("supervirus_wiped_out", holder.player_id, card_id)
            )
            continue
        if holder.pending_orders.pop("supervirus_serum", False):
            holder.pending_orders.pop("supervirus", None)
            events.append(EngineEvent("supervirus_cured", holder.player_id, card_id))
            continue
        if not isinstance(order, dict):
            events.extend(_retain(holder, infection))
            continue
        target_id = str(order.get("target", ""))
        source_id = str(infection.get("source", ""))
        if not _can_pass(state, holder.player_id, target_id, source_id):
            events.append(
                EngineEvent(
                    "supervirus_pass_failed",
                    holder.player_id,
                    card_id,
                    {"target": target_id},
                )
            )
            events.extend(_retain(holder, infection))
            continue
        holder.pending_orders.pop("supervirus", None)
        loss = _infect(state, target_id, card_id, holder.player_id)
        started.add(target_id)
        events.append(
            EngineEvent(
                "supervirus_passed",
                holder.player_id,
                card_id,
                {"target": target_id, "loss": loss},
            )
        )
    return events


def _infect(
    state: GameState,
    target_id: str,
    card_id: str,
    source_id: str,
) -> int:
    target = state.players[target_id]
    loss = remove_population_with_bank(state, target_id, roll_nuke_die(state.rng, True))
    target.pending_orders["supervirus"] = {
        "card": card_id,
        "source": source_id,
        "turns_held": 1,
    }
    return loss


def _retain(holder: PlayerState, infection: dict[str, object]) -> list[EngineEvent]:
    card_id = str(infection.get("card", ""))
    turns = _turn_count(infection.get("turns_held", 0)) + 1
    if turns < 4:
        infection["turns_held"] = turns
        return [
            EngineEvent(
                "supervirus_retained",
                holder.player_id,
                card_id,
                {"turns_held": turns},
            )
        ]
    holder.pending_orders.pop("supervirus", None)
    holder.pending_orders["supervirus_immunity"] = True
    return [EngineEvent("supervirus_immunity", holder.player_id, card_id)]


def _turn_count(value: object) -> int:
    if type(value) is int:
        return value
    if isinstance(value, str) and value.isdecimal():
        return int(value)
    return 0


def _is_immune(state: GameState, target_id: str) -> bool:
    return bool(state.players[target_id].pending_orders.get("supervirus_immunity"))


def _can_pass(
    state: GameState,
    holder_id: str,
    target_id: str,
    source_id: str,
) -> bool:
    if target_id not in state.players or target_id == holder_id:
        return False
    if not state.players[target_id].alive:
        return False
    if _is_immune(state, target_id):
        return False
    alive_count = sum(player.alive for player in state.players.values())
    return alive_count <= 2 or target_id != source_id


__all__ = ["apply_supervirus_orders"]
