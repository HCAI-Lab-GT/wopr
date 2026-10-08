"""Equipment targeting helpers for launch resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nuclear_war_env.fallout import FalloutOutcome
from nuclear_war_env.state import GameState, PlayerState

from .events import EngineEvent
from .war_state import declare_war


def resolve_equipment_target(
    state: GameState,
    attacker_id: str,
    delivery_id: str,
    order: dict[str, Any],
    outcome: FalloutOutcome,
) -> list[EngineEvent] | None:
    target_spec = order.get("equipment_target")
    if not isinstance(target_spec, dict):
        return None
    equipment = _targeted_equipment(state, target_spec)
    if equipment is None:
        return [_failed(attacker_id, delivery_id)]
    declare_war(state)
    if outcome.attacker_backfire or outcome.yield_multiplier == 0:
        return [
            EngineEvent(
                "equipment_target_missed",
                attacker_id,
                delivery_id,
                equipment.payload,
            )
        ]
    equipment.record["status"] = "destroyed"
    return [
        EngineEvent(
            "equipment_destroyed",
            attacker_id,
            delivery_id,
            equipment.payload,
        )
    ]


@dataclass(frozen=True)
class _EquipmentTarget:
    owner_id: str
    payload: dict[str, object]
    record: dict[str, Any]


def _targeted_equipment(
    state: GameState,
    target_spec: dict[Any, Any],
) -> _EquipmentTarget | None:
    owner_id = target_spec.get("owner")
    kind = target_spec.get("kind")
    equipment_id = target_spec.get("id")
    if not isinstance(owner_id, str) or owner_id not in state.players:
        return None
    if not isinstance(kind, str) or not isinstance(equipment_id, str):
        return None
    inventory = _equipment_inventory(state.players[owner_id], kind)
    record = inventory.get(equipment_id)
    if not isinstance(record, dict) or not _is_targetable(kind, record):
        return None
    payload: dict[str, object] = {
        "target_player": owner_id,
        "kind": kind,
        "equipment": equipment_id,
    }
    return _EquipmentTarget(owner_id, payload, record)


def _equipment_inventory(player: PlayerState, kind: str) -> dict[str, Any]:
    if kind == "atomic_cannon":
        return player.pending_orders.get("atomic_cannons", {})
    if kind == "submarine":
        return player.pending_orders.get("submarine_states", {})
    return {}


def _is_targetable(kind: str, record: dict[str, Any]) -> bool:
    if record.get("status") == "destroyed":
        return False
    if kind == "submarine":
        return record.get("status") == "exposed"
    return kind == "atomic_cannon"


def _failed(attacker_id: str, delivery_id: str) -> EngineEvent:
    return EngineEvent(
        "equipment_target_failed",
        attacker_id,
        delivery_id,
        {"reason": "invalid_equipment_target"},
    )


__all__ = ["resolve_equipment_target"]
