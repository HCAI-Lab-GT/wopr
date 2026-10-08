"""Postal Parallel environment action-selection tests."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_env.actions import ActionType, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.env_postal import PostalParallelEnv
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_parallel_step_uses_pre_step_legal_actions_for_all_players() -> None:
    delivery = Card("delivery", CardCategory.DELIVERY, "Delivery")
    warhead = Card("warhead", CardCategory.WARHEAD, "Warhead", value=10)
    propaganda = Card(
        "propaganda",
        CardCategory.PROPAGANDA,
        "Propaganda",
        metadata={"value_millions": 5},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["player_0", "player_1"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards([delivery, warhead, propaganda])
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["player_0"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": None,
        }
    }
    state.players["player_1"].hand = ["propaganda"]
    env = PostalParallelEnv(seed=0)
    env.reset()
    env.game_state = state
    env.agents = ["player_0", "player_1"]

    p0_actions = legal_actions(state, "player_0", "postal")
    p1_actions = legal_actions(state, "player_1", "postal")
    p0_target = _index_of(p0_actions, ActionType.TARGET)
    p1_propaganda = _index_of(p1_actions, ActionType.POSTAL_PROPAGANDA)

    _, _, _, _, infos = env.step({"player_0": p0_target, "player_1": p1_propaganda})

    assert infos["player_1"]["events"] == ["postal_propaganda_ordered"]


def test_parallel_env_waits_for_pending_final_strike_before_done() -> None:
    cards = [
        Card("delivery_a", CardCategory.DELIVERY, "Delivery A"),
        Card("warhead_a", CardCategory.WARHEAD, "Warhead A", value=30),
        Card(
            "delivery_b",
            CardCategory.DELIVERY,
            "Delivery B",
            metadata={"capacity": 1},
        ),
        Card("warhead_b", CardCategory.WARHEAD, "Warhead B", value=15),
    ]
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["player_0", "player_1"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["player_0"].hand = ["delivery_b", "warhead_b"]
    state.players["player_1"].pending_orders["launches"] = {
        "delivery_a": {
            "delivery": "delivery_a",
            "capacity": 1,
            "warheads": ["warhead_a"],
            "target": "player_0",
        }
    }
    env = PostalParallelEnv(seed=0)
    env.reset()
    env.game_state = state
    env.agents = ["player_0", "player_1"]

    observations, _, terminations, _, _ = env.step({"player_0": 0, "player_1": 0})

    assert state.players["player_0"].pending_orders.get("final_strike")
    assert observations
    assert not any(terminations.values())

    _, _, final_terminations, _, _ = env.step({"player_0": 0, "player_1": 0})

    assert sum(state.players["player_1"].population) < 30
    assert all(final_terminations.values())


def test_parallel_step_rejects_masked_action_index() -> None:
    env = PostalParallelEnv(seed=0)
    observations, _ = env.reset()
    invalid_action = _first_masked_action(observations["player_0"]["action_mask"])

    with pytest.raises(ValueError, match="Invalid action index"):
        env.step({"player_0": invalid_action, "player_1": 0})


def test_parallel_step_requires_live_agent_actions() -> None:
    env = PostalParallelEnv(seed=0)
    env.reset()

    with pytest.raises(ValueError, match="Missing action for live agent player_1"):
        env.step({"player_0": 0})


def test_parallel_step_rejects_unknown_agent_actions() -> None:
    env = PostalParallelEnv(seed=0)
    env.reset()

    with pytest.raises(ValueError, match="Unknown action agent: player_2"):
        env.step({"player_0": 0, "player_1": 0, "player_2": 0})


def test_parallel_step_rejects_non_dictionary_actions() -> None:
    malformed_actions: Any = None
    env = PostalParallelEnv(seed=0)
    env.reset()

    with pytest.raises(ValueError, match="Parallel actions must be a dictionary"):
        env.step(malformed_actions)


def _index_of(actions, action_type: ActionType) -> int:
    return next(
        index
        for index, action in enumerate(actions)
        if action.action_type is action_type
    )


def _first_masked_action(mask) -> int:
    return next(index for index, value in enumerate(mask) if int(value) == 0)
