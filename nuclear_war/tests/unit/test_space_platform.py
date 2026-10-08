"""Postal space platform tests."""

from __future__ import annotations

from collections import Counter

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.replay_event_player_references import (
    validate_event_player_references,
)
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _build_state(seed: int = 0) -> GameState:
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.POSTAL, players=players, draw_pile=[])
    state.rng = SeededRNG(seed=seed)
    state.population_bank = [10, 5]
    return state


def test_space_platform_launch_stores_warheads() -> None:
    state = _build_state()  # seed 0 -> Radioactive Fallout die 4 (success)
    state.players["p1"].pending_orders["space_platform_launch"] = [
        {"platform": "platform1", "warheads": [10, 20]}
    ]
    events = execute_postal_turn(state)
    platform = state.players["p1"].pending_orders["space_platforms"]["platform1"]
    assert platform["warheads"] == [10, 20]
    assert any(event.event_type == "space_platform_launched" for event in events)
    # Launch uses the 6-sided Radioactive Fallout die, not the two-d10 spinner.
    die = next(e for e in events if e.event_type == "fallout_die_result")
    assert die.card_id == "platform1"
    assert die.payload["raw_result"] == 4
    assert die.payload["cloud"] is False
    assert "spinner_result" not in [e.event_type for e in events]


def test_space_platform_launch_rejects_float_warhead_payload() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["space_platform_launch"] = [
        {"platform": "platform1", "warheads": [10.0]}
    ]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "platform1" not in state.players["p1"].pending_orders["space_platforms"]
    assert "spinner_result" not in event_types
    assert "space_platform_launched" not in event_types


def test_space_platform_drop_uses_one_warhead() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10, 20]}
    }
    state.players["p1"].pending_orders["space_platform_drop"] = [
        {"platform": "platform1", "target": "p2"}
    ]
    events = execute_postal_turn(state)
    platform = state.players["p1"].pending_orders["space_platforms"]["platform1"]
    assert platform["warheads"] == [20]
    assert sum(state.players["p2"].population) == 20
    assert Counter(state.population_bank) == Counter([25])
    assert any(event.event_type == "space_platform_dropped" for event in events)


def test_space_platform_drop_rejects_float_stored_warhead() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10.0]}
    }
    state.players["p1"].pending_orders["space_platform_drop"] = [
        {"platform": "platform1", "target": "p2"}
    ]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]
    platform = state.players["p1"].pending_orders["space_platforms"].get("platform1")

    assert platform is not None
    assert platform["warheads"] == [10.0]
    assert sum(state.players["p2"].population) == 30
    assert "spinner_result" not in event_types
    assert "space_platform_dropped" not in event_types


def test_space_platform_drop_skips_eliminated_target_before_spinner() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10, 20]}
    }
    state.players["p1"].pending_orders["space_platform_drop"] = [
        {"platform": "platform1", "target": "p2"}
    ]
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]
    platform = state.players["p1"].pending_orders["space_platforms"]["platform1"]

    assert "spinner_result" not in event_types
    assert "space_platform_dropped" not in event_types
    assert state.peace
    assert platform["warheads"] == [10, 20]


def test_space_shuttle_reloads_existing_platform() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10]}
    }
    state.players["p1"].pending_orders["space_shuttle_reload"] = [
        {"platform": "platform1", "warheads": [20, 50]}
    ]
    events = execute_postal_turn(state)
    platform = state.players["p1"].pending_orders["space_platforms"]["platform1"]
    assert platform["warheads"] == [10, 20, 50]
    assert any(event.event_type == "space_shuttle_reloaded" for event in events)


def test_space_shuttle_attack_does_not_require_existing_platform() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["space_shuttle_attack"] = [
        {"shuttle": "shuttle1", "target": "p2", "warheads": [10]}
    ]
    events = execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 20
    assert Counter(state.population_bank) == Counter([25])
    assert not state.peace
    assert any(event.event_type == "space_shuttle_attacked" for event in events)


def test_space_shuttle_attack_skips_eliminated_target_before_spinner() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["space_shuttle_attack"] = [
        {"shuttle": "shuttle1", "target": "p2", "warheads": [10]}
    ]
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "spinner_result" not in event_types
    assert "space_shuttle_attacked" not in event_types
    assert state.peace


def test_space_platform_double_failure_crashes_into_owner() -> None:
    state = _build_state(seed=316)  # die rolls cloud, cloud (1, 1)
    state.players["p1"].pending_orders["space_platform_launch"] = [
        {"platform": "platform1", "warheads": [10]}
    ]
    events = execute_postal_turn(state)
    platforms = state.players["p1"].pending_orders["space_platforms"]
    assert "platform1" not in platforms
    assert sum(state.players["p1"].population) == 20
    assert Counter(state.population_bank) == Counter([25])
    assert any(event.event_type == "space_platform_crashed" for event in events)
    dice = [e for e in events if e.event_type == "fallout_die_result"]
    assert [e.payload["raw_result"] for e in dice] == [1, 1]
    assert all(e.payload["cloud"] is True for e in dice)


def test_space_platform_single_cloud_fails_without_crash() -> None:
    state = _build_state(seed=14)  # die rolls cloud then non-cloud (1, then >=2)
    state.players["p1"].pending_orders["space_platform_launch"] = [
        {"platform": "platform1", "warheads": [10]}
    ]
    events = execute_postal_turn(state)
    platforms = state.players["p1"].pending_orders["space_platforms"]
    event_types = [event.event_type for event in events]
    assert "platform1" not in platforms
    assert sum(state.players["p1"].population) == 30  # first cloud loses no population
    assert "space_platform_launch_failed" in event_types
    assert "space_platform_crashed" not in event_types
    dice = [e for e in events if e.event_type == "fallout_die_result"]
    assert dice[0].payload["cloud"] is True
    assert dice[1].payload["cloud"] is False


def test_space_platform_crash_killing_owner_logs_elimination() -> None:
    # The owner holds only 10M, so the double-cloud crash (-10M) zeroes them. The
    # crash branch must log the elimination like every other warhead death, or the
    # replay breaks its own _validate_eliminations_have_events invariant (a dead
    # player with no player_eliminated event).
    state = _build_state(seed=316)
    state.players["p1"].population = [10]
    state.players["p1"].pending_orders["space_platform_launch"] = [
        {"platform": "platform1", "warheads": [10]}
    ]

    events = execute_postal_turn(state)

    assert any(event.event_type == "space_platform_crashed" for event in events)
    assert not state.players["p1"].alive
    assert sum(state.players["p1"].population) == 0

    eliminations = [
        event
        for event in events
        if event.event_type == "player_eliminated" and event.player_id == "p1"
    ]
    assert len(eliminations) == 1
    # A targetless self-crash has no attacker and no target, yet the replay schema
    # forbids both a self and a null `by`; the only legal attribution is another
    # player, and V1 picks the top living opponent (== the retaliation target).
    assert eliminations[0].payload == {"by": "p2"}
    # The emitted attribution must pass the real replay player-reference validator.
    validate_event_player_references(
        {
            "event_type": "player_eliminated",
            "player_id": "p1",
            "payload": dict(eliminations[0].payload),
        },
        0,
        {"p1", "p2"},
    )


def test_space_platform_crash_killing_owner_schedules_final_retaliation() -> None:
    # Postal rules phase 3 grants a final strike to any player whose population is
    # destroyed except by propaganda. A launch-pad crash destroys the owner's
    # population, so their surviving delivery + warhead must be pooled into a
    # queued final-strike order aimed at the eliminator.
    state = _build_state(seed=316)
    state.players["p1"].population = [10]
    state.register_cards(
        [
            Card("missile", CardCategory.DELIVERY, "Missile", metadata={"capacity": 1}),
            Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
        ]
    )
    state.players["p1"].hand = ["missile", "warhead"]
    state.players["p1"].pending_orders["space_platform_launch"] = [
        {"platform": "platform1", "warheads": [10]}
    ]

    execute_postal_turn(state)

    assert not state.players["p1"].alive
    final_strike = state.players["p1"].pending_orders.get("final_strike")
    assert final_strike
    assert any(
        order.get("delivery") == "missile"
        and order.get("warheads") == ["warhead"]
        and order.get("eliminated_by") == "p2"
        for order in final_strike
    )
    # The queued final strike blocks peace restoration, so the mark set by the
    # elimination bookkeeping survives the peace phase.
    assert state.players["p1"].pending_orders.get("peace_restore_pending")


def test_space_platform_crash_killing_last_owner_attributes_to_dead_seat() -> None:
    # If the crash makes the owner the final casualty (every opponent already dead),
    # there is no living opponent to attribute to -- but the replay still forbids a
    # self or null `by`, so the elimination falls back to a known (dead) seat and
    # remains replay-legal.
    state = _build_state(seed=316)
    state.players["p1"].population = [10]
    state.players["p2"].alive = False
    state.players["p2"].population = []
    state.players["p1"].pending_orders["space_platform_launch"] = [
        {"platform": "platform1", "warheads": [10]}
    ]

    events = execute_postal_turn(state)

    assert not state.players["p1"].alive
    eliminations = [
        event
        for event in events
        if event.event_type == "player_eliminated" and event.player_id == "p1"
    ]
    assert len(eliminations) == 1
    assert eliminations[0].payload == {"by": "p2"}
    validate_event_player_references(
        {
            "event_type": "player_eliminated",
            "player_id": "p1",
            "payload": dict(eliminations[0].payload),
        },
        0,
        {"p1", "p2"},
    )


def test_crash_killed_owner_does_not_execute_queued_drop() -> None:
    # Seed 2 double-clouds the launch (fallout_die cloud twice) -> crash self-kill.
    from nuclear_war_env.engine.postal.space_platform import apply_space_platform_orders
    from nuclear_war_env.rng import SeededRNG
    from nuclear_war_env.state import GameState, Ruleset, create_players

    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=10),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=2)
    state.population_bank = [10, 5]
    state.players["p1"].population = [10]  # crash removes 10M -> eliminated
    state.players["p2"].population = [30]
    # An already-aloft platform the queued drop would use, plus the crashing launch.
    state.players["p1"].pending_orders["space_platforms"] = {"old": {"warheads": [10]}}
    state.players["p1"].pending_orders["space_platform_launch"] = [
        {"platform": "new", "warheads": [10]}
    ]
    state.players["p1"].pending_orders["space_platform_drop"] = [
        {"platform": "old", "target": "p2"}
    ]

    events = apply_space_platform_orders(state)
    types = [e.event_type for e in events]

    assert not state.players["p1"].alive
    assert "player_eliminated" in types  # crash self-kill still logged
    assert "space_platform_dropped" not in types  # dead owner does not drop
    assert sum(state.players["p2"].population) == 30  # target undamaged
    # Robust discriminator: pre-fix _drop calls declare_war() unconditionally; the
    # crash self-kill never declares war, so post-fix peace is intact regardless of
    # whether the (skipped) drop would have hit or missed.
    assert state.peace is True
