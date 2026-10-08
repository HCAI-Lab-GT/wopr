"""Player observation hidden-information tests."""

from __future__ import annotations

from nuclear_war_env.observation import to_player_observation
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_observation_hides_opponent_face_down_card_ids() -> None:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    opponent = state.players["p2"]
    opponent.face_down_queue.clear()
    opponent.face_down_queue.extend(["hidden_delivery", "hidden_warhead"])

    observation = to_player_observation(state, "p1")

    public_opponent = observation["players"]["p2"]
    assert public_opponent["face_down_count"] == 2
    assert "face_down_queue" not in public_opponent
    assert "hidden_delivery" not in str(observation)
    assert "hidden_warhead" not in str(observation)


def test_observation_hides_opponent_postal_pending_orders() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.players["p2"].pending_orders = {
        "launches": {
            "hidden_delivery": {
                "target": "p1",
                "warheads": ["hidden_warhead"],
            }
        },
        "press": ["private_message"],
    }

    observation = to_player_observation(state, "p1")

    public_opponent = observation["players"]["p2"]
    assert "pending_orders" not in public_opponent
    assert "hidden_delivery" not in str(observation)
    assert "hidden_warhead" not in str(observation)
    assert "private_message" not in str(observation)


def test_observation_shows_only_self_deterrent_card_ids() -> None:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.players["p1"].deterrents = ["own_deterrent", None]
    state.players["p2"].deterrents = ["hidden_deterrent", None]

    observation = to_player_observation(state, "p1")

    assert observation["self"]["deterrents"] == ["own_deterrent", None]
    public_opponent = observation["players"]["p2"]
    assert public_opponent["deterrent_count"] == 1
    assert "deterrents" not in public_opponent
    assert "hidden_deterrent" not in str(observation)


def test_observation_shows_only_self_pending_orders_copy() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.players["p1"].pending_orders = {
        "launches": {"own_delivery": {"target": "p2", "warheads": ["own_warhead"]}}
    }
    state.players["p2"].pending_orders = {
        "launches": {
            "hidden_delivery": {
                "target": "p1",
                "warheads": ["hidden_warhead"],
            }
        }
    }

    observation = to_player_observation(state, "p1")

    own_orders = observation["self"]["pending_orders"]
    own_orders["launches"]["own_delivery"]["target"] = "changed"
    assert (
        state.players["p1"].pending_orders["launches"]["own_delivery"]["target"] == "p2"
    )
    assert "pending_orders" not in observation["players"]["p2"]
    assert "own_delivery" in str(observation)
    assert "hidden_delivery" not in str(observation)
    assert "hidden_warhead" not in str(observation)


def test_observation_shows_only_self_final_strike_cards_copy() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.players["p1"].final_strike_cards = ["own_warhead"]
    state.players["p2"].final_strike_cards = ["hidden_warhead"]

    observation = to_player_observation(state, "p1")

    own_cards = observation["self"]["final_strike_cards"]
    own_cards.append("changed")
    assert state.players["p1"].final_strike_cards == ["own_warhead"]
    assert "final_strike_cards" not in observation["players"]["p2"]
    assert "own_warhead" in str(observation)
    assert "hidden_warhead" not in str(observation)
