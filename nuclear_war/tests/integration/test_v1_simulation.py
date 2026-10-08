"""Integration tests for v1 simulations."""

from __future__ import annotations

import pytest

from nuclear_war_env.simulation import SimulationConfig, run_simulation


def test_table_simulation_plays_a_full_turn_per_player_each_round() -> None:
    config = SimulationConfig(
        mode="table", players=3, seed=5, agent="random", max_turns=6
    )
    result = run_simulation(config)
    actions_by_player_turn: dict[tuple[str, int], set[str]] = {}
    for action in result["actions"]:
        key = (action["player_id"], action["turn"])
        actions_by_player_turn.setdefault(key, set()).add(action["action_type"])
    # The faithful turn model performs several ordered steps for one player within
    # a single turn (draw / slide / place), unlike the old one-action-per-turn loop.
    assert any(len(types) >= 2 for types in actions_by_player_turn.values())
    assert any(
        {"advance", "enqueue"} <= types for types in actions_by_player_turn.values()
    )


def test_table_simulation_resolves_secrets_drawn_during_play() -> None:
    resolution_events = {
        "secret_triggered",
        "secret_population_stolen",
        "secret_population_gained",
        "secret_population_damaged",
        "secret_turns_lost",
    }
    saw_resolution = False
    for seed in range(6):
        config = SimulationConfig(
            mode="table", players=3, seed=seed, agent="random", max_turns=40
        )
        result = run_simulation(config)
        event_types = {event["event_type"] for event in result["events"]}
        if event_types & resolution_events:
            saw_resolution = True
    # Secrets drawn during play are resolved, not left as inert 'secret_queued'.
    assert saw_resolution


def test_table_simulation_resolves_propaganda_during_peace() -> None:
    saw_propaganda = False
    for seed in range(6):
        config = SimulationConfig(
            mode="table", players=3, seed=seed, agent="random", max_turns=40
        )
        result = run_simulation(config)
        event_types = {event["event_type"] for event in result["events"]}
        if "propaganda_effect" in event_types:
            saw_propaganda = True
    # Propaganda steals population during peace, not just queues inertly.
    assert saw_propaganda


def test_table_eliminations_always_match_zero_population() -> None:
    # A player killed mid-turn by a chain reaction must stop acting: no dead player
    # may end with population, and no zero-population player may stay "alive".
    for seed in (7, 37, 59):
        for agent in ("heuristic", "random"):
            config = SimulationConfig(
                mode="table", players=3, seed=seed, agent=agent, max_turns=80
            )
            result = run_simulation(config)
            eliminated = set(result["eliminations"])
            for player_id, population in result["final_populations"].items():
                assert (population == 0) == (player_id in eliminated), (
                    f"seed={seed} agent={agent} {player_id} pop={population} "
                    f"eliminated={player_id in eliminated}"
                )


def test_table_random_simulation_is_reproducible() -> None:
    config = SimulationConfig(
        mode="table", players=3, seed=7, agent="random", max_turns=8
    )
    first = run_simulation(config)
    second = run_simulation(config)
    assert first == second
    assert first["mode"] == "table"
    assert first["active_variant"]["variant_id"] == "base_later_two_d10"
    # Final strikes can now wipe everyone, so mutual annihilation is also valid.
    assert first["termination_reason"] in {
        "one_player_remaining",
        "no_players_remaining",
        "max_turns",
    }
    assert len(first["actions"]) > 0
    assert all(1 <= event["turn"] <= first["turns"] for event in first["events"])


def test_postal_heuristic_simulation_disables_press() -> None:
    config = SimulationConfig(
        mode="postal",
        players=3,
        seed=11,
        agent="heuristic",
        max_turns=6,
        press=False,
    )
    result = run_simulation(config)
    event_types = [event["event_type"] for event in result["events"]]
    assert result["mode"] == "postal"
    assert "press_entry" not in event_types
    assert result["agent"] == "heuristic"


def test_postal_simulation_rejects_press_mode() -> None:
    config = SimulationConfig(
        mode="postal",
        players=3,
        seed=11,
        agent="heuristic",
        max_turns=6,
        press=True,
    )
    with pytest.raises(ValueError, match="Postal press is deferred"):
        run_simulation(config)


def test_simulation_rejects_unknown_mode() -> None:
    config = SimulationConfig(
        mode="space",
        players=2,
        seed=11,
        agent="random",
        max_turns=1,
    )
    with pytest.raises(ValueError, match="Unknown mode: space"):
        run_simulation(config)


def test_simulation_rejects_invalid_player_count_before_loading_rules(
    monkeypatch,
) -> None:
    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    config = SimulationConfig(
        mode="table",
        players=1,
        seed=11,
        agent="random",
        max_turns=1,
    )
    with pytest.raises(ValueError, match="At least two players are required"):
        run_simulation(config)


def test_simulation_rejects_unknown_agent_before_loading_rules(monkeypatch) -> None:
    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid config")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=11,
        agent="scripted",
        max_turns=1,
    )
    with pytest.raises(ValueError, match="Unknown agent: scripted"):
        run_simulation(config)


def test_simulation_rejects_non_positive_max_turns() -> None:
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=11,
        agent="random",
        max_turns=0,
    )
    with pytest.raises(ValueError, match="At least one turn is required"):
        run_simulation(config)


def test_table_simulation_can_end_with_one_player_remaining() -> None:
    config = SimulationConfig(
        mode="table",
        players=3,
        seed=2,
        agent="heuristic",
        max_turns=60,
    )
    result = run_simulation(config)
    assert result["termination_reason"] == "one_player_remaining"
    # Exactly one survivor with positive population; everyone else eliminated.
    # Assert the invariant, not a seed-fragile winner id / population.
    survivors = [
        player_id
        for player_id, population in result["final_populations"].items()
        if population > 0
    ]
    assert survivors == [result["winner"]]
    assert result["winner"] is not None
    assert all(
        population == 0
        for player_id, population in result["final_populations"].items()
        if player_id != result["winner"]
    )


def test_table_simulation_uses_null_player_for_non_player_events() -> None:
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=3,
        agent="heuristic",
        max_turns=50,
    )
    result = run_simulation(config)
    known_players = set(result["final_populations"])
    assert all(
        event["player_id"] is None or event["player_id"] in known_players
        for event in result["events"]
    )
    assert any(
        event["event_type"] == "peace_restored" and event["player_id"] is None
        for event in result["events"]
    )
