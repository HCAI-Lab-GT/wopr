from __future__ import annotations

from pytest import MonkeyPatch

from nuclear_war_env.engine.decision import DecisionCursor, TurnPhase
from nuclear_war_env.fallout import FalloutOutcome, SpinnerEffect
from nuclear_war_env.state import GameState


def queue_final_strike(state: GameState) -> None:
    player = state.players["player_1"]
    player.alive = False
    player.population = []
    player.pending_orders["final_strike"] = [
        {
            "delivery": "retaliation_delivery",
            "warheads": ["retaliation_warhead"],
            "target": None,
            "eliminated_by": "player_0",
        }
    ]
    state.cursor = DecisionCursor("player_0", TurnPhase.ATTACK)
    state.cursor.round_pending = set(state.players)


def no_radiation(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "nuclear_war_env.engine.launch.spin_spinner",
        lambda rng: (40, FalloutOutcome(SpinnerEffect.NO_RADIATION)),
    )


__all__ = ["no_radiation", "queue_final_strike"]
