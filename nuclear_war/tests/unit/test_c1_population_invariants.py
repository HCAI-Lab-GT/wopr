"""C1 population-bank invariant tests."""

from __future__ import annotations

from dataclasses import asdict

from nuclear_war_env.engine.launch_resolution import trigger_global_loss
from nuclear_war_env.observation import observe, to_player_observation
from nuclear_war_env.setup_game import create_game_state
from nuclear_war_env.simulation import SimulationConfig, run_simulation
from nuclear_war_env.state import GameState


def test_global_loss_conserves_seeded_table_population_deck() -> None:
    state = create_game_state("table", player_count=3, seed=1)
    _assert_population_deck_conserved(state)

    trigger_global_loss(state, "player_0", "player_1")

    _assert_population_deck_conserved(state)
    assert all(not player.alive for player in state.players.values())


def test_table_replay_final_populations_remain_integer_totals() -> None:
    result = run_simulation(
        SimulationConfig(
            mode="table",
            players=3,
            seed=1,
            agent="heuristic",
            max_turns=3,
        )
    )

    assert set(result["final_populations"]) == {"player_0", "player_1", "player_2"}
    assert all(type(value) is int for value in result["final_populations"].values())
    assert "population_bank" not in result["final_populations"]


def test_observations_do_not_expose_population_bank_contents() -> None:
    state = create_game_state("table", player_count=3, seed=1)
    state.population_bank = [25, 10, 5]

    typed_observation = observe(state, "player_0")
    dict_observation = to_player_observation(state, "player_0")

    assert "population_bank" not in asdict(typed_observation)
    assert "population_bank" not in dict_observation


def _assert_population_deck_conserved(state: GameState) -> None:
    assert _population_deck_total(state) == 240


def _population_deck_total(state: GameState) -> int:
    return sum(state.population_bank) + sum(
        sum(player.population) for player in state.players.values()
    )
