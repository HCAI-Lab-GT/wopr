"""Constructed mutual-annihilation and final-strike chain tests (audit gaps)."""

from __future__ import annotations

from pytest import MonkeyPatch

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.launch import execute_launches
from nuclear_war_env.fallout import resolve_spinner
from nuclear_war_env.state import GameState, Ruleset, create_players


def _force_plain_damage(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nuclear_war_env.engine.launch.spin_spinner",
        lambda rng: (40, resolve_spinner(40)),  # 36-49: no radiation modifier
    )


def _arsenal(state: GameState, owner: str) -> list[str]:
    cards = [
        Card(
            f"{owner}_missile",
            CardCategory.DELIVERY,
            "Missile",
            metadata={"capacity": 1},
        ),
        Card(f"{owner}_warhead", CardCategory.WARHEAD, "Warhead", value=10),
    ]
    state.register_cards(cards)
    return [card.identifier for card in cards]


def _state(player_ids: list[str]) -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(player_ids, starting_population=10),
        draw_pile=[],
    )
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    return state


def _launch(state: GameState, attacker: str, target: str) -> None:
    delivery, warhead = _arsenal(state, attacker)
    state.players[attacker].pending_orders["launches"] = {
        delivery: {
            "delivery": delivery,
            "capacity": 1,
            "warheads": [warhead],
            "target": target,
        }
    }


def test_two_player_mutual_annihilation(monkeypatch: MonkeyPatch) -> None:
    state = _state(["player_0", "player_1"])
    _force_plain_damage(monkeypatch)
    _launch(state, "player_0", "player_1")
    state.players["player_1"].hand = _arsenal(state, "player_1_ret")

    events = execute_launches(state)

    assert all(not player.alive for player in state.players.values())
    order = [
        (event.event_type, event.player_id)
        for event in events
        if event.event_type in {"player_eliminated", "final_strike_executed"}
    ]
    assert order == [
        ("player_eliminated", "player_1"),
        ("final_strike_executed", "player_1"),
        ("player_eliminated", "player_0"),
        # player_0 keeps the retaliation privilege but has no living opponent,
        # so its final strike is a no-op event.
        ("final_strike_executed", "player_0"),
    ]


def test_three_player_final_strike_chain_retaliates_in_turn(
    monkeypatch: MonkeyPatch,
) -> None:
    # player_0 kills player_1; player_1's final strike targets the eliminator
    # and kills player_0; the chain-eliminated player_0 also retaliates, at the
    # only living opponent player_2.
    state = _state(["player_0", "player_1", "player_2"])
    _force_plain_damage(monkeypatch)
    _launch(state, "player_0", "player_1")
    state.players["player_1"].hand = _arsenal(state, "player_1_ret")
    state.players["player_0"].hand = _arsenal(state, "player_0_ret")

    events = execute_launches(state)

    assert all(not player.alive for player in state.players.values())
    order = [
        (event.event_type, event.player_id)
        for event in events
        if event.event_type in {"player_eliminated", "final_strike_executed"}
    ]
    assert order == [
        ("player_eliminated", "player_1"),
        ("final_strike_executed", "player_1"),
        ("player_eliminated", "player_0"),
        ("final_strike_executed", "player_0"),
        ("player_eliminated", "player_2"),
    ]
    eliminated_by = {
        event.player_id: event.payload["by"]
        for event in events
        if event.event_type == "player_eliminated"
    }
    assert eliminated_by == {
        "player_1": "player_0",
        "player_0": "player_1",
        "player_2": "player_0",
    }
