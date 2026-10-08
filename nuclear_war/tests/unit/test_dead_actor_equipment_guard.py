"""A dead actor must not execute its queued equipment/action orders."""

from __future__ import annotations

from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _postal_state(seed: int = 0) -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=seed)
    state.population_bank = [10, 5]
    return state


def test_dead_owner_submarine_order_is_skipped() -> None:
    from nuclear_war_env.engine.postal.submarine import apply_submarine_orders

    state = _postal_state()
    state.players["p1"].alive = False
    # A valid at-sea sub that WOULD fire (spinner_result is emitted before any
    # hit/miss branch, so its absence robustly proves the corpse was skipped).
    state.players["p1"].pending_orders["submarine_states"] = {
        "s1": {"status": "at_sea", "warhead_yield": 10, "target": "p2"}
    }
    state.players["p1"].pending_orders["submarines"] = [{"submarine": "s1"}]
    events = apply_submarine_orders(state)
    assert all(e.event_type != "spinner_result" for e in events)
    assert sum(state.players["p2"].population) == 30
    assert state.peace is True  # no submarine_strike -> no declare_war


def test_dead_owner_sabotage_order_is_skipped() -> None:
    from nuclear_war_env.engine.postal.sabotage import apply_sabotage_orders

    state = _postal_state()
    state.players["p2"].pending_orders["launches"] = {
        "d1": {"delivery": "d1", "warheads": ["w1"], "target": "p1"}
    }
    state.players["p1"].alive = False
    state.players["p1"].pending_orders["sabotage"] = [
        {"target": "p2", "delivery": "d1"}
    ]
    events = apply_sabotage_orders(state)
    assert events == []  # dead saboteur does not act
    assert "d1" in state.players["p2"].pending_orders["launches"]  # launch survives
