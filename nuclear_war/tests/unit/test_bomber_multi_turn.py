"""Bomber multi-turn attack fidelity tests (rules: attack until payload is dropped)."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_launches
from nuclear_war_env.engine.draw import resolve_face_up_card
from nuclear_war_env.engine.launch_helpers import can_load_warhead
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, PlayerState, Ruleset, create_players

# Seed 9's first spinner rolls are 59, 78, 47 (plain damage bands: no dud,
# backfire, or intercept-relevant modifier). Seed 31's first roll is 1
# (booster explodes / bomber runs out of fuel band).
_DAMAGE_SEED = 9
_BACKFIRE_SEED = 31


def _bomber_state(payload: int = 20, warhead_value: int = 10) -> GameState:
    cards = [
        Card(
            "bomber",
            CardCategory.DELIVERY,
            "B-70 Bomber",
            metadata={"max_yield_megatons": payload},
        ),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=warhead_value),
        Card("warhead_2", CardCategory.WARHEAD, "Warhead 2", value=warhead_value),
        Card("filler", CardCategory.PROPAGANDA, "Filler", metadata={"value": 1}),
    ]
    players = create_players(["p1"], starting_population=10)
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=players,
        draw_pile=[],
        rng=SeededRNG(seed=_DAMAGE_SEED),
    )
    state.register_cards(cards)
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["p2"] = PlayerState(player_id="p2", population=[25, 5])
    state.players["p1"].pending_orders["launches"] = {
        "bomber": {
            "delivery": "bomber",
            "capacity": payload,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }
    state.players["p1"].pending_orders["pending_delivery"] = "bomber"
    return state


def test_bomber_persists_with_remaining_payload_after_attack() -> None:
    state = _bomber_state(payload=20, warhead_value=10)
    execute_launches(state)
    launches = state.players["p1"].pending_orders["launches"]
    assert "bomber" in launches
    assert launches["bomber"]["warheads"] == []
    assert launches["bomber"]["dropped"] == 10
    assert launches["bomber"]["target"] is None
    discarded = {card.identifier for card in state.discard_pile}
    assert "warhead" in discarded
    assert "bomber" not in discarded


def test_bomber_discarded_when_payload_exhausted() -> None:
    state = _bomber_state(payload=10, warhead_value=10)
    execute_launches(state)
    assert "launches" not in state.players["p1"].pending_orders
    discarded = {card.identifier for card in state.discard_pile}
    assert {"bomber", "warhead"} <= discarded


def test_bomber_discarded_when_it_runs_out_of_fuel() -> None:
    state = _bomber_state(payload=20, warhead_value=10)
    state.rng = SeededRNG(seed=_BACKFIRE_SEED)
    execute_launches(state)
    assert "launches" not in state.players["p1"].pending_orders
    discarded = {card.identifier for card in state.discard_pile}
    assert {"bomber", "warhead"} <= discarded


def test_bomber_discarded_when_intercepted() -> None:
    state = _bomber_state(payload=20, warhead_value=10)
    defense = Card(
        "defense",
        CardCategory.ANTIMISSILE,
        "Defense",
        metadata={"intercept": "any"},
    )
    state.register_cards([defense])
    state.players["p2"].pending_orders["defense"] = ["defense"]
    execute_launches(state)
    assert "launches" not in state.players["p1"].pending_orders
    discarded = {card.identifier for card in state.discard_pile}
    assert {"bomber", "warhead"} <= discarded


def test_can_load_warhead_counts_dropped_payload() -> None:
    state = _bomber_state(payload=20, warhead_value=10)
    launch: dict[str, object] = {"delivery": "bomber", "warheads": [], "dropped": 10}
    assert can_load_warhead(state, "bomber", launch, state.card_by_id("warhead_2"))
    launch["dropped"] = 20
    assert not can_load_warhead(state, "bomber", launch, state.card_by_id("warhead_2"))


def test_bomber_reloads_next_turn_then_expires_on_non_warhead() -> None:
    state = _bomber_state(payload=20, warhead_value=10)
    player = state.players["p1"]
    execute_launches(state)
    # Next turn: a warhead turns up and loads onto the persisting bomber.
    player.face_up = "warhead_2"
    event = resolve_face_up_card(state, player, previous=None)
    assert event is not None and event.event_type == "warhead_loaded"
    assert player.pending_orders["launches"]["bomber"]["warheads"] == ["warhead_2"]
    player.pending_orders["launches"]["bomber"]["target"] = "p2"
    execute_launches(state)
    assert "launches" not in player.pending_orders
    assert "bomber" in {card.identifier for card in state.discard_pile}


def test_bomber_expires_when_non_warhead_turns_up_after_attack() -> None:
    state = _bomber_state(payload=20, warhead_value=10)
    player = state.players["p1"]
    execute_launches(state)
    player.face_up = "filler"
    resolve_face_up_card(state, player, previous=None)
    assert "bomber" in {card.identifier for card in state.discard_pile}
    assert "bomber" not in player.pending_orders.get("launches", {})
