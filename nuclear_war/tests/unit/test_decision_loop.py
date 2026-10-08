# tests/unit/test_decision_loop.py
from __future__ import annotations

from nuclear_war_agents.baseline import HeuristicAgent, RandomAgent
from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.agent_protocol import as_decision_agent
from nuclear_war_env.decision_loop import (
    apply_decision,
    pending_decision,
    run_decisions,
    start_game,
)
from nuclear_war_env.engine.decision import DecisionType
from nuclear_war_env.observation import Observation, PrivatePlayerObservation
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.setup_game import create_game_state


def _observation() -> Observation:
    return Observation(
        player_id="player_0",
        ruleset="table",
        turn=0,
        peace=True,
        self=PrivatePlayerObservation(
            population=0,
            hand=[],
            secrets=[],
            deterrents=[],
            face_up=None,
            face_down_queue=[],
            final_strike_cards=[],
            pending_orders={},
            alive=True,
            at_war=False,
        ),
        players={},
        draw_count=0,
        discard_count=0,
    )


def test_adapter_lets_heuristic_pick_first_of_homogeneous_options() -> None:
    options = [
        build_action("player_0", ActionType.ENQUEUE, "Place a", {"cards": ["a"]}),
        build_action("player_0", ActionType.ENQUEUE, "Place b", {"cards": ["b"]}),
    ]
    agent = as_decision_agent(HeuristicAgent(SeededRNG(0)))
    assert agent.choose(observation=_observation(), options=options) is options[0]


def test_adapter_lets_random_choose_a_legal_option() -> None:
    options = [
        build_action("player_0", ActionType.ENQUEUE, "Place a", {"cards": ["a"]}),
        build_action("player_0", ActionType.ENQUEUE, "Place b", {"cards": ["b"]}),
    ]
    agent = as_decision_agent(RandomAgent(SeededRNG(3)))
    assert agent.choose(observation=_observation(), options=options) in options


def test_first_decision_is_player_0_secret_target() -> None:
    # Seed 0 deals player_0 two starting secrets: a gain-from-bank secret (auto-
    # resolved to the drawer, no decision) and an offensive "loss of turn" secret.
    # Since A2's SECRETS phase, that offensive secret surfaces as the FIRST decision
    # — a SECRET_TARGET for player_0 — ahead of any PLACE.
    state = create_game_state("table", player_count=3, seed=0)
    start_game(state)
    decision = pending_decision(state)
    assert decision is not None
    assert decision.agent_id == "player_0"
    assert decision.decision_type is DecisionType.SECRET_TARGET
    # Options are one secret_target per living opponent (highest-population first).
    assert decision.options
    assert all(o.action_type.value == "secret_target" for o in decision.options)
    assert all("card" in o.payload and "target" in o.payload for o in decision.options)


def test_apply_place_then_reaches_a_following_decision_for_some_player() -> None:
    state = create_game_state("table", player_count=3, seed=0)
    start_game(state)
    first = pending_decision(state)
    # Since A2's SECRETS phase the first decision can be a SECRET_TARGET (seed 0's
    # player_0 has a parked offensive secret) rather than a PLACE; either is a valid
    # starting decision to apply.
    assert first is not None and first.decision_type in {
        DecisionType.PLACE,
        DecisionType.SECRET_TARGET,
    }
    events = apply_decision(state, first.options[0])
    assert isinstance(events, list)
    nxt = pending_decision(state)
    # The game continues: a place/attack decision for player_0 or the next player's
    # decision — never stuck on the same already-applied choice.
    assert nxt is not None
    assert nxt.decision_type in {
        DecisionType.PLACE,
        DecisionType.LAUNCH_TARGET,
        DecisionType.MODIFY_DETERRENT,
        DecisionType.SECRET_TARGET,
        DecisionType.PROPAGANDA_TARGET,
    }
    assert not (nxt.agent_id == first.agent_id and nxt is first)


def test_full_game_terminates_with_a_single_or_no_survivor() -> None:
    state = create_game_state("table", player_count=3, seed=2)
    start_game(state)
    agents = {
        pid: as_decision_agent(HeuristicAgent(SeededRNG(2))) for pid in state.players
    }
    run_decisions(state, agents, max_turns=200)
    assert pending_decision(state) is None  # reached a terminal state
    survivors = [p for p in state.players.values() if p.alive]
    assert len(survivors) <= 1
