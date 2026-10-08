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
from nuclear_war_env.engine.propaganda_resolution import apply_propaganda_steal
from nuclear_war_env.engine.secret_resolution import is_self_secret
from nuclear_war_env.engine.target_policy import (
    highest_population_opponent,
    opponents_by_population,
)
from nuclear_war_env.replay_action_payload_validation import validate_action_payload
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.setup_game import create_game_state
from nuclear_war_env.state import GameState, Ruleset, create_players
from nuclear_war_env.table_turn import TurnResult


def test_new_decision_action_and_phase_members_exist() -> None:
    assert DecisionType.SECRET_TARGET.value == "secret_target"
    assert DecisionType.PROPAGANDA_TARGET.value == "propaganda_target"
    assert TurnPhase.SECRETS.value == "secrets"
    assert TurnPhase.PROPAGANDA.value == "propaganda"
    assert ActionType.SECRET_TARGET.value == "secret_target"
    assert ActionType.PROPAGANDA_TARGET.value == "propaganda_target"


def test_heuristic_picks_first_secret_target_option_without_rng() -> None:
    options = [
        build_action(
            "p0", ActionType.SECRET_TARGET, "at p1", {"card": "s", "target": "p1"}
        ),
        build_action(
            "p0", ActionType.SECRET_TARGET, "at p2", {"card": "s", "target": "p2"}
        ),
    ]
    rng = SeededRNG(0)
    agent = HeuristicAgent(rng)
    # Pick is deterministic and is the FIRST option (engine ordered highest-pop first).
    assert agent.choose(options) is options[0]
    assert agent.choose(options) is options[0]


def test_heuristic_picks_first_propaganda_target_option() -> None:
    options = [
        build_action(
            "p0", ActionType.PROPAGANDA_TARGET, "from p1", {"card": "c", "target": "p1"}
        ),
        build_action(
            "p0", ActionType.PROPAGANDA_TARGET, "from p2", {"card": "c", "target": "p2"}
        ),
    ]
    agent = HeuristicAgent(SeededRNG(0))
    assert agent.choose(options) is options[0]


def test_random_can_pick_any_secret_target_option() -> None:
    options = [
        build_action(
            "p0", ActionType.SECRET_TARGET, "at p1", {"card": "s", "target": "p1"}
        ),
        build_action(
            "p0", ActionType.SECRET_TARGET, "at p2", {"card": "s", "target": "p2"}
        ),
    ]
    agent = RandomAgent(SeededRNG(3))
    assert agent.choose(options) in options


def _three_player_state(pops: dict[str, int]) -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(list(pops), starting_population=0),
        draw_pile=[],
    )
    for pid, total in pops.items():
        state.players[pid].population = [total] if total else []
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    return state


def test_opponents_ordered_highest_population_first() -> None:
    state = _three_player_state({"player_0": 10, "player_1": 30, "player_2": 20})
    assert opponents_by_population(state, "player_0") == ["player_1", "player_2"]
    # First element equals the legacy single-target policy exactly.
    assert opponents_by_population(state, "player_0")[0] == highest_population_opponent(
        state, "player_0"
    )


def test_opponents_tie_breaks_by_player_order() -> None:
    state = _three_player_state({"player_0": 5, "player_1": 20, "player_2": 20})
    assert opponents_by_population(state, "player_0") == ["player_1", "player_2"]
    assert highest_population_opponent(state, "player_0") == "player_1"


def test_opponents_excludes_dead_and_self() -> None:
    state = _three_player_state({"player_0": 5, "player_1": 0, "player_2": 7})
    # player_1 has 0 population; create_players marks alive via population — force dead.
    state.players["player_1"].alive = False
    assert opponents_by_population(state, "player_0") == ["player_2"]
    assert opponents_by_population(state, "player_2") == ["player_0"]


def test_is_self_secret_true_only_for_gain_from_bank() -> None:
    gain = Card(
        "g", CardCategory.SECRET, "Gain", metadata={"gain_from_bank_millions": 5}
    )
    offensive = Card(
        "o", CardCategory.SECRET, "Steal", metadata={"steal_population_millions": 5}
    )
    assert is_self_secret(gain) is True
    assert is_self_secret(offensive) is False


def test_apply_propaganda_steal_moves_population_and_logs() -> None:
    state = _three_player_state({"player_0": 10, "player_1": 30, "player_2": 20})
    state.register_cards(
        [
            Card(
                "prop",
                CardCategory.PROPAGANDA,
                "Propaganda",
                metadata={"value_millions": 5},
            )
        ]
    )
    events = apply_propaganda_steal(state, "player_0", "prop", "player_1")
    assert sum(state.players["player_0"].population) == 15
    assert sum(state.players["player_1"].population) == 25
    assert any(e.event_type == "propaganda_effect" for e in events)


def test_apply_propaganda_steal_to_zero_eliminates_without_retaliation() -> None:
    state = _three_player_state({"player_0": 10, "player_1": 4, "player_2": 20})
    state.register_cards(
        [
            Card(
                "prop",
                CardCategory.PROPAGANDA,
                "Propaganda",
                metadata={"value_millions": 9},
            )
        ]
    )
    events = apply_propaganda_steal(state, "player_0", "prop", "player_1")
    assert not state.players["player_1"].alive
    assert any(
        e.event_type == "player_eliminated" and e.player_id == "player_1"
        for e in events
    )
    assert not state.players["player_1"].pending_orders.get("final_strike")


def _action_dict(action_type: str, payload: dict) -> dict:
    return {
        "action_type": action_type,
        "payload": payload,
        "turn": 1,
        "player_id": "player_0",
    }


def test_replay_accepts_secret_and_propaganda_target_actions() -> None:
    # validate_card_target_payload checks "card" identifies a card; use real card ids
    # from the base registry.
    validate_action_payload(
        _action_dict(
            "secret_target", {"card": "nw_base_b6794c74", "target": "player_1"}
        ),
        0,
    )
    validate_action_payload(
        _action_dict(
            "propaganda_target", {"card": "nw_base_b3a2b1d5", "target": "player_2"}
        ),
        0,
    )


def test_replay_rejects_malformed_secret_target_action() -> None:
    with pytest.raises(ValueError):
        validate_action_payload(
            _action_dict("secret_target", {"target": "player_1"}), 0
        )


def _drive_to_first_decision_of_type(state, want: DecisionType, agents, cap=2000):
    """Advance the loop until a decision of `want` appears or the game ends."""
    for _ in range(cap):
        d = pending_decision(state)
        if d is None:
            return None
        if d.decision_type is want:
            return d
        action = agents[d.agent_id].choose(None, d.options)
        apply_decision(state, action)
    raise AssertionError("decision not reached")


def test_offensive_secret_surfaces_as_secret_target_decision() -> None:
    # Find a seed/turn where a player draws an offensive secret; drive with heuristic.
    state = create_game_state("table", player_count=3, seed=1)
    start_game(state)
    agents = {
        pid: as_decision_agent(HeuristicAgent(SeededRNG(1))) for pid in state.players
    }
    d = _drive_to_first_decision_of_type(state, DecisionType.SECRET_TARGET, agents)
    if d is not None:  # not every seed draws an offensive secret early; tolerate None
        assert all(o.action_type.value == "secret_target" for o in d.options)
        assert all("card" in o.payload and "target" in o.payload for o in d.options)


def test_secret_target_options_are_ordered_highest_population_first() -> None:
    # Construct a deterministic state with a parked offensive secret and known pops.
    state = _three_player_state({"player_0": 5, "player_1": 30, "player_2": 20})
    state.register_cards(
        [
            Card(
                "sx",
                CardCategory.SECRET,
                "Steal",
                metadata={"steal_population_millions": 3},
            )
        ]
    )
    state.players["player_0"].secrets = ["sx"]
    state.cursor = DecisionCursor(turn_player="player_0", phase=TurnPhase.SECRETS)
    state.cursor.round_pending = set(state.players)
    _advance(state, _RoundStamper(TurnResult()))
    d = pending_decision(state)
    assert d is not None and d.decision_type is DecisionType.SECRET_TARGET
    assert [o.payload["target"] for o in d.options] == ["player_1", "player_2"]


def test_propaganda_surfaces_as_decision_in_peace_and_drops_in_war() -> None:
    # Peace: a propaganda card surfaces a PROPAGANDA_TARGET decision (highest-pop).
    state = _three_player_state({"player_0": 5, "player_1": 30, "player_2": 20})
    state.peace = True
    state.register_cards(
        [
            Card(
                "pp",
                CardCategory.PROPAGANDA,
                "Propaganda",
                metadata={"value_millions": 4},
            )
        ]
    )
    state.players["player_0"].pending_orders["propaganda"] = ["pp"]
    state.cursor = DecisionCursor(turn_player="player_0", phase=TurnPhase.PROPAGANDA)
    state.cursor.round_pending = set(state.players)
    _advance(state, _RoundStamper(TurnResult()))
    d = pending_decision(state)
    assert d is not None and d.decision_type is DecisionType.PROPAGANDA_TARGET
    assert [o.payload["target"] for o in d.options] == ["player_1", "player_2"]

    # War: propaganda is dropped with no decision (advances past PROPAGANDA).
    state2 = _three_player_state({"player_0": 5, "player_1": 30, "player_2": 20})
    state2.peace = False
    state2.register_cards(
        [
            Card(
                "pp",
                CardCategory.PROPAGANDA,
                "Propaganda",
                metadata={"value_millions": 4},
            )
        ]
    )
    state2.players["player_0"].pending_orders["propaganda"] = ["pp"]
    state2.cursor = DecisionCursor(turn_player="player_0", phase=TurnPhase.PROPAGANDA)
    state2.cursor.round_pending = set(state2.players)
    # This degenerate state (all players alive, empty draw/discard, empty hands) never
    # reaches a natural terminal, so stop at the first round boundary — that is past
    # PROPAGANDA, which is all this case asserts (war drops the card, no decision).
    _advance(state2, _RoundStamper(TurnResult()), stop_at_round_boundary=True)
    d2 = pending_decision(state2)
    assert d2 is None or d2.decision_type is not DecisionType.PROPAGANDA_TARGET
    assert "propaganda" not in state2.players["player_0"].pending_orders
