"""Initial setup integration tests for Nuclear War v1."""

from __future__ import annotations

from nuclear_war_env.simulation import SimulationConfig, run_simulation


def test_table_simulation_starts_with_initial_face_down_cards() -> None:
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=7,
        agent="heuristic",
        max_turns=1,
    )
    result = run_simulation(config)

    # Since the setup/peace fidelity pass the opening face-down commitment is an
    # agent decision, so the log opens with two setup_place actions per player
    # (seat order) before any turn action.
    setup_actions = result["actions"][: 2 * config.players]
    assert [a["action_type"] for a in setup_actions] == ["setup_place"] * 4
    assert [a["player_id"] for a in setup_actions] == (
        ["player_0", "player_0", "player_1", "player_1"]
    )
    # Seed 7 deals player_0 two offensive starting secrets. Since A2's SECRETS phase
    # those resolve (in rules order: draw -> secrets -> slide -> place) ahead of the
    # slide, so the first post-setup action is a secret_target, not the advance.
    first_action = result["actions"][2 * config.players]
    assert first_action["player_id"] == "player_0"
    assert first_action["action_type"] == "secret_target"
    # Player_0's first turn is a full turn: the secrets resolve, the initial face-down
    # launch track is advanced, and a new card is placed (not a single micro-action).
    player_0_turn_1 = [
        action["action_type"]
        for action in result["actions"]
        if action["player_id"] == "player_0" and action["turn"] == 1
    ]
    assert "advance" in player_0_turn_1
    assert "enqueue" in player_0_turn_1
