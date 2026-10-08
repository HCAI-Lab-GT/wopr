"""Final retaliation firing and target assignment (table mode)."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.cards_registry import (
    CardRecord,
    CardType,
    build_deck_from_registry,
)
from nuclear_war_env.engine.launch_helpers import (
    assign_retaliation_targets,
    schedule_final_retaliation,
)
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state(ruleset: Ruleset = Ruleset.TABLE) -> GameState:
    state = GameState(
        ruleset=ruleset,
        players=create_players(
            ["player_0", "player_1", "player_2"], starting_population=30
        ),
        draw_pile=[],
    )
    state.register_cards(
        [
            Card(
                "delivery", CardCategory.DELIVERY, "Missile", metadata={"capacity": 1}
            ),
            Card("warhead", CardCategory.WARHEAD, "Warhead 10 Mt", value=10),
        ]
    )
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    return state


def _eliminate_with_arsenal(state: GameState, player_id: str) -> None:
    player = state.players[player_id]
    player.hand = ["delivery", "warhead"]
    player.population = []
    player.alive = False


def test_final_retaliation_actually_fires() -> None:
    state = _state(Ruleset.TABLE)
    _eliminate_with_arsenal(state, "player_1")

    events = schedule_final_retaliation(
        state, state.players["player_1"], eliminated_by="player_0"
    )

    event_types = [event.event_type for event in events]
    assert "final_strike_executed" in event_types
    # A spinner_result only appears if a launch was actually resolved — proving
    # the retaliation fired rather than being skipped for want of a target.
    assert "spinner_result" in event_types


def test_assign_retaliation_targets_prefers_the_eliminator() -> None:
    state = _state(Ruleset.TABLE)
    orders = [{"delivery": "d", "warheads": ["w"], "target": None}]

    assign_retaliation_targets(state, "player_1", orders, "player_0")

    assert orders[0]["target"] == "player_0"


def test_retaliation_falls_back_to_richest_when_eliminator_dead() -> None:
    state = _state(Ruleset.TABLE)
    state.players["player_0"].alive = False  # eliminator already gone
    state.players["player_2"].population = [25, 10]  # richest survivor
    orders = [{"delivery": "d", "warheads": ["w"], "target": None}]

    assign_retaliation_targets(state, "player_1", orders, "player_0")

    assert orders[0]["target"] == "player_2"


def test_retaliation_pool_includes_face_down_queue_cards() -> None:
    # Rules: combine EACH acceptable delivery system and warhead card you
    # possess — face-down strategy cards included.
    state = _state(Ruleset.TABLE)
    player = state.players["player_1"]
    player.population = []
    player.alive = False
    player.face_down_queue[0] = "delivery"
    player.face_down_queue[1] = "warhead"

    schedule_final_retaliation(
        state, player, eliminated_by="player_0", auto_resolve_table=False
    )

    orders = player.pending_orders["final_strike"]
    assert len(orders) == 1
    assert orders[0]["delivery"] == "delivery"
    assert orders[0]["warheads"] == ["warhead"]


def test_retaliation_pool_includes_deterrent_cards() -> None:
    state = _state(Ruleset.TABLE)
    player = state.players["player_1"]
    player.population = []
    player.alive = False
    player.deterrents[0] = "delivery"
    player.deterrents[1] = "warhead"

    schedule_final_retaliation(
        state, player, eliminated_by="player_0", auto_resolve_table=False
    )

    orders = player.pending_orders["final_strike"]
    assert len(orders) == 1
    assert orders[0]["delivery"] == "delivery"
    assert orders[0]["warheads"] == ["warhead"]


def test_retaliation_pool_loads_hand_warheads_before_queue_warheads() -> None:
    state = _state(Ruleset.TABLE)
    state.register_cards(
        [Card("warhead_queue", CardCategory.WARHEAD, "Warhead 10 Mt", value=10)]
    )
    player = state.players["player_1"]
    player.population = []
    player.alive = False
    player.hand = ["delivery", "warhead"]
    player.face_down_queue[0] = "warhead_queue"

    schedule_final_retaliation(
        state, player, eliminated_by="player_0", auto_resolve_table=False
    )

    orders = player.pending_orders["final_strike"]
    assert orders[0]["warheads"] == ["warhead"]


def test_final_strike_keeps_same_base_delivery_copies_separate() -> None:
    registry = {
        "missile": CardRecord(
            "missile",
            "Missile",
            CardType.CARRIER,
            2,
            {"max_yield_megatons": 10, "intercept_by": []},
        ),
        "warhead": CardRecord(
            "warhead",
            "Warhead 10",
            CardType.WARHEAD,
            2,
            {"yield_megatons": 10},
        ),
    }
    deck = build_deck_from_registry(registry)
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1", "p2"], 30),
        draw_pile=[],
    )
    state.register_cards(deck)
    player = state.players["p1"]
    player.hand = [card.identifier for card in deck]

    schedule_final_retaliation(
        state,
        player,
        eliminated_by="p2",
        auto_resolve_table=False,
    )

    orders = player.pending_orders["final_strike"]
    assert len(orders) == 2
    assert {order["delivery"] for order in orders} == {
        "missile__copy_01",
        "missile__copy_02",
    }


def test_pure_engine_postal_final_strike_fires_at_deterministic_target() -> None:
    from nuclear_war_env.cards import Card, CardCategory
    from nuclear_war_env.engine.postal.handlers_early import phase_final_strike
    from nuclear_war_env.rng import SeededRNG
    from nuclear_war_env.state import GameState, Ruleset, create_players

    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(
        [
            Card("d", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
            Card("w", CardCategory.WARHEAD, "Warhead", value=30),
        ]
    )
    # p1 has a pooled, hand-assembled retaliation order with NO target (the bug).
    state.players["p1"].pending_orders["final_strike"] = [
        {"delivery": "d", "warheads": ["w"], "target": None, "eliminated_by": "p2"}
    ]

    events = phase_final_strike(state)
    types = [e.event_type for e in events]

    assert "final_strike_executed" in types
    # The retaliation now resolves against p2 (the eliminator) instead of vanishing.
    assert sum(state.players["p2"].population) < 30
    assert "final_strike" not in state.players["p1"].pending_orders  # consumed
