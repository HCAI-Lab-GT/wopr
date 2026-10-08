from __future__ import annotations

from pytest import MonkeyPatch

from nuclear_war_env.decision_loop import (
    _advance,
    _RoundStamper,
    apply_decision,
    pending_decision,
)
from nuclear_war_env.engine.decision import DecisionCursor, TurnPhase
from nuclear_war_env.engine.launch import execute_launches
from nuclear_war_env.fallout import FalloutOutcome, SpinnerEffect
from nuclear_war_env.state import GameState
from nuclear_war_env.table_turn import TurnResult


def test_filtered_execute_launches_clears_dead_targets_for_other_attackers(
    retaliation_state: GameState,
) -> None:
    retaliation_state.players["player_2"].population = []
    retaliation_state.players["player_2"].alive = False
    retaliation_state.players["player_1"].pending_orders["launches"] = {
        "attack_delivery": {
            "delivery": "attack_delivery",
            "capacity": 1,
            "warheads": ["attack_warhead"],
            "target": "player_2",
        }
    }

    execute_launches(
        retaliation_state,
        use_hand_intercept=False,
        auto_resolve_final_strike=False,
        only_attacker_id="player_2",
        only_delivery_id="retaliation_delivery",
    )

    launch = retaliation_state.players["player_1"].pending_orders["launches"][
        "attack_delivery"
    ]
    assert launch["target"] is None


def test_filtered_execute_launches_preserves_later_attacker_dead_targets(
    retaliation_state: GameState,
) -> None:
    retaliation_state.players["player_2"].population = []
    retaliation_state.players["player_2"].alive = False
    retaliation_state.players["player_1"].pending_orders["launches"] = {
        "attack_delivery": {
            "delivery": "attack_delivery",
            "capacity": 1,
            "warheads": ["attack_warhead"],
            "target": "player_2",
        }
    }

    execute_launches(
        retaliation_state,
        use_hand_intercept=False,
        auto_resolve_final_strike=False,
        only_attacker_id="player_0",
        only_delivery_id="retaliation_delivery",
    )

    launch = retaliation_state.players["player_1"].pending_orders["launches"][
        "attack_delivery"
    ]
    assert launch["target"] == "player_2"


def test_dead_target_final_strike_launch_is_cleared_after_prior_launch(
    monkeypatch: MonkeyPatch,
    retaliation_state: GameState,
) -> None:
    monkeypatch.setattr(
        "nuclear_war_env.engine.launch.spin_spinner",
        lambda rng: (40, FalloutOutcome(SpinnerEffect.NO_RADIATION)),
    )
    retaliation_state.players["player_0"].population = [5]
    player = retaliation_state.players["player_1"]
    player.alive = False
    player.population = []
    player.pending_orders["final_strike"] = [
        {
            "delivery": "attack_delivery",
            "warheads": ["attack_warhead"],
            "target": "player_0",
        },
        {
            "delivery": "retaliation_delivery",
            "warheads": ["retaliation_warhead"],
            "target": "player_0",
        },
    ]
    retaliation_state.cursor = DecisionCursor("player_0", TurnPhase.ATTACK)
    retaliation_state.cursor.round_pending = set(retaliation_state.players)
    _advance(retaliation_state, _RoundStamper(TurnResult()), True)
    intercept = pending_decision(retaliation_state)
    assert intercept is not None

    apply_decision(retaliation_state, intercept.options[-1])

    assert not player.pending_orders.get("launches")
