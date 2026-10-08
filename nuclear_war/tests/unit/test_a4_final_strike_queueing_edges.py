from __future__ import annotations

from pytest import MonkeyPatch

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.launch import execute_launches
from nuclear_war_env.engine.launch_helpers import schedule_final_retaliation
from nuclear_war_env.fallout import FalloutOutcome, SpinnerEffect
from nuclear_war_env.state import GameState


def test_table_queue_mode_does_not_promote_blocked_duplicate_delivery(
    retaliation_state: GameState,
) -> None:
    retaliation_state.card_lookup["retaliation_delivery"] = Card(
        "retaliation_delivery",
        CardCategory.DELIVERY,
        "Retaliation Missile",
        metadata={"capacity": 1, "max_yield_megatons": 20},
    )
    retaliation_state.register_cards(
        [
            Card("queued_warhead", CardCategory.WARHEAD, "Queued Warhead", value=15),
        ]
    )
    target = retaliation_state.players["player_1"]
    target.population = []
    target.alive = False
    target.hand = [
        "retaliation_delivery",
        "attack_warhead",
        "retaliation_warhead",
    ]
    target.pending_orders["launches"] = {
        "attack_delivery": {
            "delivery": "attack_delivery",
            "capacity": 1,
            "warheads": ["queued_warhead"],
            "target": None,
        },
        "retaliation_delivery": {
            "delivery": "retaliation_delivery",
            "capacity": 1,
            "warheads": [],
            "target": None,
        },
    }
    target.pending_orders["pending_delivery"] = "retaliation_delivery"

    schedule_final_retaliation(
        retaliation_state,
        target,
        eliminated_by="player_0",
        auto_resolve_table=False,
    )

    orders = target.pending_orders["final_strike"]
    assert [order["delivery"] for order in orders] == ["attack_delivery"]
    assert [order["warheads"] for order in orders] == [["queued_warhead"]]


def test_execute_launches_queues_final_strike_without_running_it(
    monkeypatch: MonkeyPatch,
    retaliation_state: GameState,
) -> None:
    retaliation_state.players["player_1"].hand = [
        "retaliation_delivery",
        "retaliation_warhead",
    ]
    retaliation_state.players["player_1"].population = [5]
    retaliation_state.players["player_0"].pending_orders["launches"] = {
        "attack_delivery": {
            "delivery": "attack_delivery",
            "capacity": 1,
            "warheads": ["attack_warhead"],
            "target": "player_1",
        }
    }

    monkeypatch.setattr(
        "nuclear_war_env.engine.launch.spin_spinner",
        lambda rng: (40, FalloutOutcome(SpinnerEffect.NO_RADIATION)),
    )

    events = execute_launches(retaliation_state, auto_resolve_final_strike=False)

    assert [event.event_type for event in events].count("player_eliminated") == 1
    assert "final_strike_executed" not in [event.event_type for event in events]
    assert retaliation_state.players["player_1"].pending_orders.get("final_strike")


def test_table_queue_mode_preserves_dead_pretargeted_launch(
    retaliation_state: GameState,
) -> None:
    target = retaliation_state.players["player_1"]
    target.population = []
    target.alive = False
    retaliation_state.players["player_2"].population = []
    retaliation_state.players["player_2"].alive = False
    target.pending_orders["launches"] = {
        "attack_delivery": {
            "delivery": "attack_delivery",
            "capacity": 1,
            "warheads": ["attack_warhead"],
            "target": "player_2",
        }
    }

    schedule_final_retaliation(
        retaliation_state,
        target,
        eliminated_by="player_0",
        auto_resolve_table=False,
    )

    order = target.pending_orders["final_strike"][0]
    assert order["target"] == "player_2"
