"""Supervirus postal mechanic tests."""

from __future__ import annotations

from collections import Counter

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.postal.handlers_misc import phase_cruise_move
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state() -> GameState:
    cards = [Card("virus", CardCategory.SPECIAL, "Supervirus")]
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2", "p3"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    state.population_bank = [1]
    return state


def test_supervirus_start_damages_target_and_tracks_holder() -> None:
    state = _state()
    state.players["p1"].pending_orders["supervirus_start"] = {
        "card": "virus",
        "target": "p2",
    }

    events = phase_cruise_move(state)

    assert sum(state.players["p2"].population) == 26
    assert state.players["p2"].pending_orders["supervirus"] == {
        "card": "virus",
        "source": "p1",
        "turns_held": 1,
    }
    assert any(event.event_type == "supervirus_started" for event in events)


def test_supervirus_start_skips_eliminated_target() -> None:
    state = _state()
    state.players["p1"].pending_orders["supervirus_start"] = {
        "card": "virus",
        "target": "p2",
    }
    state.players["p2"].alive = False
    state.players["p2"].population.clear()

    events = phase_cruise_move(state)

    assert "supervirus" not in state.players["p2"].pending_orders
    assert not any(event.event_type == "supervirus_started" for event in events)


def test_supervirus_start_returns_population_cards_to_bank() -> None:
    state = _state()
    state.players["p2"].population = [5]
    state.players["p1"].pending_orders["supervirus_start"] = {
        "card": "virus",
        "target": "p2",
    }

    events = phase_cruise_move(state)

    assert state.players["p2"].population == [1]
    assert Counter(state.population_bank) == Counter([5])
    assert any(
        event.event_type == "supervirus_started" and event.payload.get("loss") == 4
        for event in events
    )


def test_supervirus_passes_to_new_holder_and_damages_recipient() -> None:
    state = _state()
    state.players["p2"].pending_orders["supervirus"] = {
        "card": "virus",
        "source": "p1",
        "turns_held": 1,
    }
    state.players["p2"].pending_orders["supervirus_pass"] = {"target": "p3"}

    events = phase_cruise_move(state)

    assert "supervirus" not in state.players["p2"].pending_orders
    assert sum(state.players["p3"].population) == 26
    assert state.players["p3"].pending_orders["supervirus"] == {
        "card": "virus",
        "source": "p2",
        "turns_held": 1,
    }
    assert any(event.event_type == "supervirus_passed" for event in events)


def test_supervirus_cannot_pass_back_to_source_with_three_survivors() -> None:
    state = _state()
    state.players["p2"].pending_orders["supervirus"] = {
        "card": "virus",
        "source": "p1",
        "turns_held": 1,
    }
    state.players["p2"].pending_orders["supervirus_pass"] = {"target": "p1"}

    events = phase_cruise_move(state)

    assert state.players["p2"].pending_orders["supervirus"]["source"] == "p1"
    assert sum(state.players["p1"].population) == 30
    assert any(event.event_type == "supervirus_pass_failed" for event in events)


def test_supervirus_four_turn_retention_confers_immunity() -> None:
    state = _state()
    state.players["p2"].pending_orders["supervirus"] = {
        "card": "virus",
        "source": "p1",
        "turns_held": 3,
    }

    events = phase_cruise_move(state)

    assert "supervirus" not in state.players["p2"].pending_orders
    assert state.players["p2"].pending_orders["supervirus_immunity"] is True
    assert any(event.event_type == "supervirus_immunity" for event in events)


def test_supervirus_boolean_turns_held_retains_as_first_turn() -> None:
    state = _state()
    state.players["p2"].pending_orders["supervirus"] = {
        "card": "virus",
        "source": "p1",
        "turns_held": True,
    }

    phase_cruise_move(state)

    assert state.players["p2"].pending_orders["supervirus"]["turns_held"] == 1


def test_supervirus_is_removed_when_holder_is_eliminated() -> None:
    state = _state()
    state.players["p2"].alive = False
    state.players["p2"].population = []
    state.players["p2"].pending_orders["supervirus"] = {
        "card": "virus",
        "source": "p1",
        "turns_held": 2,
    }

    events = phase_cruise_move(state)

    assert "supervirus" not in state.players["p2"].pending_orders
    assert any(event.event_type == "supervirus_wiped_out" for event in events)


def test_superserum_removes_supervirus() -> None:
    state = _state()
    state.players["p2"].pending_orders["supervirus"] = {
        "card": "virus",
        "source": "p1",
        "turns_held": 2,
    }
    state.players["p2"].pending_orders["supervirus_serum"] = True

    events = phase_cruise_move(state)

    assert "supervirus" not in state.players["p2"].pending_orders
    assert any(event.event_type == "supervirus_cured" for event in events)
