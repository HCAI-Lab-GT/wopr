from __future__ import annotations

from nuclear_war_env.engine.launch_helpers import schedule_final_retaliation
from nuclear_war_env.state import GameState


def test_table_final_strike_can_be_queued_without_auto_firing(
    retaliation_state: GameState,
) -> None:
    target = retaliation_state.players["player_1"]
    target.hand = ["retaliation_delivery", "retaliation_warhead"]
    target.population = []
    target.alive = False

    events = schedule_final_retaliation(
        retaliation_state,
        target,
        eliminated_by="player_0",
        auto_resolve_table=False,
    )

    assert events == []
    orders = target.pending_orders["final_strike"]
    assert orders[0]["target"] is None
    assert orders[0]["eliminated_by"] == "player_0"


def test_table_queue_mode_preserves_pretargeted_launch(
    retaliation_state: GameState,
) -> None:
    target = retaliation_state.players["player_1"]
    target.population = []
    target.alive = False
    target.pending_orders["launches"] = {
        "attack_delivery": {
            "delivery": "attack_delivery",
            "capacity": 1,
            "warheads": ["attack_warhead"],
            "target": "player_2",
        }
    }

    events = schedule_final_retaliation(
        retaliation_state,
        target,
        eliminated_by="player_0",
        auto_resolve_table=False,
    )

    assert events == []
    order = target.pending_orders["final_strike"][0]
    assert order["target"] == "player_2"


def test_table_queue_mode_drops_empty_final_strike_launches(
    retaliation_state: GameState,
) -> None:
    target = retaliation_state.players["player_1"]
    target.population = []
    target.alive = False
    target.pending_orders["launches"] = {
        "attack_delivery": {
            "delivery": "attack_delivery",
            "capacity": 1,
            "warheads": [],
            "target": None,
        }
    }

    events = schedule_final_retaliation(
        retaliation_state,
        target,
        eliminated_by="player_0",
        auto_resolve_table=False,
    )

    assert events == []
    assert not target.pending_orders.get("final_strike")


def test_table_queue_mode_collapses_duplicate_delivery_like_baseline(
    retaliation_state: GameState,
) -> None:
    target = retaliation_state.players["player_1"]
    target.population = []
    target.alive = False
    target.hand = [
        "retaliation_delivery",
        "attack_delivery",
        "attack_warhead",
        "retaliation_warhead",
    ]
    target.pending_orders["launches"] = {
        "attack_delivery": {
            "delivery": "attack_delivery",
            "capacity": 1,
            "warheads": [],
            "target": None,
        }
    }
    target.pending_orders["pending_delivery"] = "attack_delivery"

    schedule_final_retaliation(
        retaliation_state,
        target,
        eliminated_by="player_0",
        auto_resolve_table=False,
    )

    orders = target.pending_orders["final_strike"]
    assert [order["delivery"] for order in orders] == [
        "attack_delivery",
        "retaliation_delivery",
    ]
    assert [order["warheads"] for order in orders] == [
        ["retaliation_warhead"],
        ["attack_warhead"],
    ]
