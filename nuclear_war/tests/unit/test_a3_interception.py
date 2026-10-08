# tests/unit/test_a3_interception.py
from __future__ import annotations

import pytest

from nuclear_war_agents.baseline import HeuristicAgent, RandomAgent
from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.agent_protocol import as_decision_agent
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.decision_loop import (
    DecisionCursor,
    _advance,
    _RoundStamper,
    apply_decision,
    pending_decision,
    start_game,
)
from nuclear_war_env.engine.decision import DecisionType, TurnPhase
from nuclear_war_env.engine.launch_helpers import (
    attempt_intercept,
    eligible_hand_antimissiles,
)
from nuclear_war_env.observation import observe
from nuclear_war_env.replay_action_payload_validation import validate_action_payload
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.setup_game import create_game_state
from nuclear_war_env.state import GameState, Ruleset, create_players
from nuclear_war_env.table_turn import TurnResult


def test_intercept_enum_members_exist() -> None:
    assert DecisionType.INTERCEPT.value == "intercept"
    assert TurnPhase.INTERCEPT.value == "intercept"
    assert ActionType.INTERCEPT.value == "intercept"


def test_heuristic_picks_first_intercept_option_without_rng() -> None:
    # Engine orders plays first, decline last; heuristic must pick the first play.
    options = [
        build_action("p1", ActionType.INTERCEPT, "Intercept with am", {"card": "am"}),
        build_action("p1", ActionType.INTERCEPT, "Decline interception", {}),
    ]
    agent = HeuristicAgent(SeededRNG(0))
    assert agent.choose(options) is options[0]
    assert agent.choose(options) is options[0]


def test_heuristic_declines_when_only_option_is_decline() -> None:
    options = [build_action("p1", ActionType.INTERCEPT, "Decline interception", {})]
    agent = HeuristicAgent(SeededRNG(0))
    assert agent.choose(options) is options[0]


def test_random_can_pick_any_intercept_option() -> None:
    options = [
        build_action("p1", ActionType.INTERCEPT, "Intercept with am", {"card": "am"}),
        build_action("p1", ActionType.INTERCEPT, "Decline interception", {}),
    ]
    agent = RandomAgent(SeededRNG(3))
    assert agent.choose(options) in options


def _intercept_state() -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["player_0", "player_1"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards(
        [
            Card("missile", CardCategory.DELIVERY, "Missile", metadata={"capacity": 1}),
            Card(
                "am",
                CardCategory.ANTIMISSILE,
                "Anti-Missile",
                metadata={"intercept": "any"},
            ),
        ]
    )
    return state


def test_use_hand_false_skips_the_hand_scan() -> None:
    state = _intercept_state()
    target = state.players["player_1"]
    target.hand = ["am"]
    delivery = state.card_by_id("missile")
    # Default (use_hand=True) intercepts from hand; use_hand=False does not.
    assert attempt_intercept(state, target, 10, delivery, use_hand=False) is None
    assert "am" in target.hand  # untouched
    assert attempt_intercept(state, target, 10, delivery, use_hand=True) == "am"


def test_use_hand_false_still_consumes_the_defense_queue() -> None:
    state = _intercept_state()
    target = state.players["player_1"]
    target.pending_orders["defense"] = ["am"]
    delivery = state.card_by_id("missile")
    assert attempt_intercept(state, target, 10, delivery, use_hand=False) == "am"
    assert target.pending_orders["defense"] == []


def test_eligible_hand_antimissiles_first_equals_attempt_intercept_pick() -> None:
    state = _intercept_state()
    state.register_cards(
        [
            Card("weak", CardCategory.ANTIMISSILE, "Weak", metadata={"intercept": 5}),
            Card(
                "anyam", CardCategory.ANTIMISSILE, "Any", metadata={"intercept": "any"}
            ),
            Card("bomb", CardCategory.WARHEAD, "Warhead", value=10),
        ]
    )
    target = state.players["player_1"]
    target.hand = ["bomb", "weak", "anyam"]  # only "anyam" stops a 10-yield strike
    delivery = state.card_by_id("missile")
    eligible = eligible_hand_antimissiles(state, target, 10, delivery)
    assert eligible == ["anyam"]
    # First eligible equals what attempt_intercept(use_hand=True) would consume.
    pick = attempt_intercept(state, target, 10, delivery, use_hand=True)
    assert eligible[0] == pick


def test_eligible_hand_antimissiles_empty_when_none_match() -> None:
    state = _intercept_state()
    state.register_cards(
        [Card("weak", CardCategory.ANTIMISSILE, "Weak", metadata={"intercept": 5})]
    )
    target = state.players["player_1"]
    target.hand = ["weak"]
    delivery = state.card_by_id("missile")
    assert eligible_hand_antimissiles(state, target, 10, delivery) == []


def _intercept_action(payload: dict) -> dict:
    return {
        "action_type": "intercept",
        "payload": payload,
        "turn": 1,
        "player_id": "player_1",
    }


def test_replay_accepts_decline_and_play_intercept_actions() -> None:
    validate_action_payload(_intercept_action({}), 0)  # decline
    # Use a real registered anti-missile card id.
    validate_action_payload(_intercept_action({"card": "nw_base_68e841fd"}), 0)


def test_replay_rejects_malformed_intercept_action() -> None:
    with pytest.raises(ValueError):
        validate_action_payload(_intercept_action({"card": "x", "extra": "y"}), 0)


def _drive_to(state, want, agents, cap=4000):
    for _ in range(cap):
        d = pending_decision(state)
        if d is None or d.decision_type is want:
            return d
        apply_decision(
            state, agents[d.agent_id].choose(observe(state, d.agent_id), d.options)
        )
    raise AssertionError("decision not reached")


def test_launch_target_is_followed_by_a_defender_intercept_decision() -> None:
    # Drive a heuristic game until a LAUNCH_TARGET, apply it, and confirm the next
    # decision is an INTERCEPT for the defender (target), always offered.
    # (apply_decision pauses AT the INTERCEPT — it does not run the loop past it,
    # so this is safe.)
    state = create_game_state("table", player_count=3, seed=7)
    start_game(state)
    agents = {
        pid: as_decision_agent(HeuristicAgent(SeededRNG(7))) for pid in state.players
    }
    d = _drive_to(state, DecisionType.LAUNCH_TARGET, agents)
    if d is not None:  # some seeds may never fire; tolerate None
        chosen = agents[d.agent_id].choose(observe(state, d.agent_id), d.options)
        target = str(chosen.payload["target"])
        apply_decision(state, chosen)
        nxt = pending_decision(state)
        assert nxt is not None
        assert nxt.decision_type is DecisionType.INTERCEPT
        assert nxt.agent_id == target  # the DEFENDER decides
        assert nxt.options  # always offered (decline at minimum)
        assert nxt.options[-1].payload == {}  # decline is last


def test_intercept_phase_builds_defender_decision_eligible_first() -> None:
    state = _intercept_state()  # player_0 vs player_1, 30 pop each
    state.register_cards([Card("w10", CardCategory.WARHEAD, "Warhead 10", value=10)])
    # A ready, targeted launch for player_0 hitting player_1; player_1 holds an
    # eligible anti-missile ("am" intercepts "any") in hand.
    state.players["player_0"].pending_orders["launches"] = {
        "missile": {
            "delivery": "missile",
            "capacity": 1,
            "warheads": ["w10"],
            "target": "player_1",
        }
    }
    state.players["player_1"].hand = ["am"]
    state.cursor = DecisionCursor(turn_player="player_0", phase=TurnPhase.INTERCEPT)
    state.cursor.round_pending = set(state.players)
    _advance(state, _RoundStamper(TurnResult()))
    d = pending_decision(state)
    assert d is not None and d.decision_type is DecisionType.INTERCEPT
    assert d.agent_id == "player_1"  # the DEFENDER decides
    assert d.options[0].payload == {"card": "am"}  # eligible play first
    assert d.options[-1].payload == {}  # decline last
