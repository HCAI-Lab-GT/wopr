from __future__ import annotations

from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.actions_deterrents import apply_deterrent_action
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.decision_loop import (
    _advance,
    _RoundStamper,
    apply_decision,
    pending_decision,
)
from nuclear_war_env.engine.decision import DecisionCursor, DecisionType, TurnPhase
from nuclear_war_env.state import GameState, Ruleset, create_players
from nuclear_war_env.table_turn import TurnResult


def _deterrent_state() -> GameState:
    cards = [
        Card("hand_a", CardCategory.WARHEAD, "Hand A", value=10),
        Card("hand_b", CardCategory.WARHEAD, "Hand B", value=20),
        Card("stored", CardCategory.DELIVERY, "Stored", metadata={"capacity": 1}),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards(cards)
    state.players["p1"].hand = ["hand_a", "hand_b"]
    state.players["p1"].deterrents = [None, "stored"]
    return state


def test_apply_deterrent_action_moves_slot_card_to_hand() -> None:
    state = _deterrent_state()
    action = build_action(
        "p1",
        ActionType.MODIFY_DETERRENT,
        "Return stored",
        {"from_slot": 1},
    )

    events = apply_deterrent_action(state, action)

    assert events == []
    assert state.players["p1"].hand == ["hand_a", "hand_b", "stored"]
    assert state.players["p1"].deterrents == [None, None]


def test_invalid_deterrent_action_leaves_state_unchanged() -> None:
    state = _deterrent_state()
    action = build_action(
        "p1",
        ActionType.MODIFY_DETERRENT,
        "Invalid occupied slot",
        {"card": "hand_a", "to_slot": 1},
    )

    events = apply_deterrent_action(state, action)

    assert events == []
    assert state.players["p1"].hand == ["hand_a", "hand_b"]
    assert state.players["p1"].deterrents == [None, "stored"]


def test_decision_loop_pauses_for_modify_deterrent_before_place() -> None:
    state = _deterrent_state()
    state.cursor = DecisionCursor("p1", TurnPhase.PROPAGANDA)
    state.cursor.round_pending = set(state.players)

    _advance(state, _RoundStamper(TurnResult()), True)

    decision = pending_decision(state)
    assert decision is not None
    assert decision.decision_type is DecisionType.MODIFY_DETERRENT
    assert decision.options[0].payload == {}


def test_skipping_modify_deterrent_advances_to_place_decision() -> None:
    state = _deterrent_state()
    state.cursor = DecisionCursor("p1", TurnPhase.PROPAGANDA)
    state.cursor.round_pending = set(state.players)
    _advance(state, _RoundStamper(TurnResult()), True)
    deterrent = pending_decision(state)
    assert deterrent is not None

    apply_decision(state, deterrent.options[0])

    place = pending_decision(state)
    assert place is not None
    assert place.decision_type is DecisionType.PLACE
    assert place.options[0].action_type is ActionType.ENQUEUE


def test_place_decision_includes_deterrent_cards_when_hand_empty() -> None:
    state = _deterrent_state()
    player = state.players["p1"]
    player.hand = []
    player.deterrents = ["stored", None]
    state.cursor = DecisionCursor("p1", TurnPhase.PLACE)
    state.cursor.round_pending = set(state.players)

    _advance(state, _RoundStamper(TurnResult()), True)

    decision = pending_decision(state)
    assert decision is not None
    assert decision.decision_type is DecisionType.PLACE
    assert decision.options[0].payload == {"cards": ["stored"]}


def test_applying_place_from_deterrent_clears_slot() -> None:
    state = _deterrent_state()
    player = state.players["p1"]
    player.hand = []
    player.deterrents = ["stored", None]
    state.cursor = DecisionCursor("p1", TurnPhase.PLACE)
    state.cursor.round_pending = set(state.players)
    _advance(state, _RoundStamper(TurnResult()), True)
    decision = pending_decision(state)
    assert decision is not None

    events = apply_decision(state, decision.options[0])

    assert [event.event_type for event in events[:1]] == ["cards_enqueued"]
    assert list(player.face_down_queue) == ["stored", None]
    assert player.deterrents == [None, None]
    assert player.hand == []
