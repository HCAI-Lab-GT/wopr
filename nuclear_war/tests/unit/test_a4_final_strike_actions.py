from __future__ import annotations

from nuclear_war_agents.baseline import HeuristicAgent, RandomAgent
from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.engine.decision import DecisionType, TurnPhase
from nuclear_war_env.engine.launch_helpers import retaliation_targets_by_policy
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState


def test_final_strike_decision_members_exist() -> None:
    assert DecisionType.FINAL_STRIKE_TARGET.value == "final_strike_target"
    assert TurnPhase.FINAL_STRIKE.value == "final_strike"
    assert ActionType.FINAL_STRIKE_TARGET.value == "final_strike_target"


def test_heuristic_picks_first_final_strike_target_without_rng() -> None:
    options = [
        build_action("p1", ActionType.FINAL_STRIKE_TARGET, "at p0", {"target": "p0"}),
        build_action("p1", ActionType.FINAL_STRIKE_TARGET, "at p2", {"target": "p2"}),
    ]
    agent = HeuristicAgent(SeededRNG(0))

    assert agent.choose(options) is options[0]
    assert agent.choose(options) is options[0]


def test_random_can_pick_any_final_strike_target() -> None:
    options = [
        build_action("p1", ActionType.FINAL_STRIKE_TARGET, "at p0", {"target": "p0"}),
        build_action("p1", ActionType.FINAL_STRIKE_TARGET, "at p2", {"target": "p2"}),
    ]
    agent = RandomAgent(SeededRNG(3))

    assert agent.choose(options) in options


def test_retaliation_targets_order_eliminator_first_then_population(
    retaliation_state: GameState,
) -> None:
    retaliation_state.players["player_2"].population = [25, 10]

    assert retaliation_targets_by_policy(
        retaliation_state,
        "player_1",
        "player_0",
    ) == ["player_0", "player_2"]


def test_retaliation_targets_fall_back_to_population_when_eliminator_dead(
    retaliation_state: GameState,
) -> None:
    retaliation_state.players["player_0"].alive = False
    retaliation_state.players["player_2"].population = [25, 10]

    assert retaliation_targets_by_policy(
        retaliation_state,
        "player_1",
        "player_0",
    ) == ["player_2"]
