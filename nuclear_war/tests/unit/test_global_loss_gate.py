"""The Super Chain Reaction gate in execute_launches (2026-07-01 audit gap)."""

from __future__ import annotations

from pytest import MonkeyPatch

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.launch import execute_launches
from nuclear_war_env.fallout import resolve_spinner
from nuclear_war_env.state import GameState, Ruleset, create_players


def _force_stockpile_explodes(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nuclear_war_env.engine.launch.spin_spinner",
        lambda rng: (97, resolve_spinner(97)),  # 95-99: stockpile explodes
    )


def _state(warhead_values: list[int]) -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(
            ["player_0", "player_1", "player_2"], starting_population=30
        ),
        draw_pile=[],
    )
    warheads = [
        Card(f"warhead_{i}", CardCategory.WARHEAD, f"Warhead {value} Mt", value=value)
        for i, value in enumerate(warhead_values)
    ]
    state.register_cards(
        [
            Card(
                "missile",
                CardCategory.DELIVERY,
                "Missile",
                metadata={"capacity": len(warheads)},
            ),
            *warheads,
        ]
    )
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["player_0"].pending_orders["launches"] = {
        "missile": {
            "delivery": "missile",
            "capacity": len(warheads),
            "warheads": [card.identifier for card in warheads],
            "target": "player_1",
        }
    }
    return state


def test_100mt_warhead_on_stockpile_explodes_triggers_global_loss(
    monkeypatch: MonkeyPatch,
) -> None:
    state = _state([100])
    _force_stockpile_explodes(monkeypatch)

    events = execute_launches(state)

    assert any(event.event_type == "global_loss" for event in events)
    assert all(not player.alive for player in state.players.values())
    eliminated = [
        event.card_id or event.player_id
        for event in events
        if event.event_type == "player_eliminated"
    ]
    assert len(eliminated) == 3


def test_100mt_total_from_smaller_warheads_does_not_trigger_global_loss(
    monkeypatch: MonkeyPatch,
) -> None:
    # The gate is per-warhead (max_single_yield >= 100), not per-launch total.
    state = _state([50, 50])
    _force_stockpile_explodes(monkeypatch)

    events = execute_launches(state)

    assert not any(event.event_type == "global_loss" for event in events)
    # Stockpile explosion still triples the 100 Mt total against the target.
    assert not state.players["player_1"].alive
    assert state.players["player_0"].alive
    assert state.players["player_2"].alive
