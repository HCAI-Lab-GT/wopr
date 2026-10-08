from __future__ import annotations

from nuclear_war_env.simulation import SimulationConfig, run_simulation

# Stage labels used below name the engine refactors these goldens track:
# A0-A6 moved every strategic choice onto the decision-point interface
# (A0 scaffolding, A2 secret/propaganda targets, A3 interception, ...),
# C1 changed population-bank change-making, and C2 gave each physical card copy
# its own runtime id.
#
# C2 golden. The A-stage decision refactors kept heuristic outcomes pinned; C2
# intentionally changes some seeds because duplicate physical card copies now
# have unique runtime ids instead of collapsing by base id.
_Golden = dict[tuple[str, int], tuple[object, str, tuple[tuple[str, int], ...]]]

HEURISTIC_C2_GOLDEN: _Golden = {
    ("heuristic", 1): (
        "player_0",
        "one_player_remaining",
        (("player_0", 75), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 2): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 81)),
    ),
    ("heuristic", 3): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 4): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 5): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 18), ("player_2", 0)),
    ),
    ("heuristic", 6): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 51)),
    ),
    ("heuristic", 7): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 8): (
        "player_0",
        "one_player_remaining",
        (("player_0", 27), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 9): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 10): (
        "player_0",
        "one_player_remaining",
        (("player_0", 40), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 11): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 69)),
    ),
    ("heuristic", 12): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 9)),
    ),
}
HEURISTIC_PRE_C2_CHANGED: _Golden = {
    ("heuristic", 5): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 6), ("player_2", 0)),
    ),
    ("heuristic", 6): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 33)),
    ),
    ("heuristic", 8): (
        "player_0",
        "one_player_remaining",
        (("player_0", 28), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 10): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 12)),
    ),
    ("heuristic", 16): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
}
RANDOM_PRE_SETUP_PEACE_GOLDEN: _Golden = {
    # Random-agent outcomes captured at df32623, immediately before the
    # 2026-07-02 setup/peace fidelity pass (SETUP_PLACE + STRATEGY_REPLACE).
    ("random", 1): (
        "player_0",
        "one_player_remaining",
        (("player_0", 109), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 2): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 62)),
    ),
    ("random", 3): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 18), ("player_2", 0)),
    ),
    ("random", 4): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 28)),
    ),
    ("random", 5): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 41), ("player_2", 0)),
    ),
    ("random", 6): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 7): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 87)),
    ),
    ("random", 8): (
        "player_0",
        "one_player_remaining",
        (("player_0", 18), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 9): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 67), ("player_2", 0)),
    ),
    ("random", 10): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 11): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 76)),
    ),
    ("random", 12): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 4), ("player_2", 0)),
    ),
}
RANDOM_A0_GOLDEN: _Golden = {
    ("random", 1): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 16), ("player_2", 0)),
    ),
    ("random", 2): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 11), ("player_2", 0)),
    ),
    ("random", 3): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 4): (
        "player_0",
        "one_player_remaining",
        (("player_0", 16), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 5): (
        "player_0",
        "one_player_remaining",
        (("player_0", 34), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 6): (
        "player_0",
        "one_player_remaining",
        (("player_0", 37), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 7): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 8): (
        "player_0",
        "one_player_remaining",
        (("player_0", 26), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 9): (
        "player_0",
        "one_player_remaining",
        (("player_0", 22), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 10): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 11): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 12): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 22), ("player_2", 0)),
    ),
}


# 4-player heuristic golden, captured before the thin-bank inexact-change
# round-down fallback. The fallback only fires when exact change is impossible,
# which never happens at 3-4 players, so these outcomes must stay pinned.
HEURISTIC_FOUR_PLAYER_GOLDEN: _Golden = {
    ("heuristic", 1): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 2): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 25), ("player_3", 0)),
    ),
    ("heuristic", 3): (
        "player_0",
        "one_player_remaining",
        (("player_0", 7), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 4): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 5): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 19), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 6): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 41), ("player_3", 0)),
    ),
    ("heuristic", 7): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 14), ("player_3", 0)),
    ),
    ("heuristic", 8): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 9): (
        "player_3",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 5)),
    ),
    ("heuristic", 10): (
        "player_3",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 15)),
    ),
    ("heuristic", 11): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 12): (
        "player_3",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 12)),
    ),
}


# Attack/retaliation fidelity golden. Model-bug removals: bombers persist across
# attacks until their payload is dropped, the final-retaliation pool includes
# face-down queue and deterrent cards, and a booster self-elimination grants
# final retaliation.
# Seeds not listed here keep their C2 (3-player) / pre-thin-bank (4-player)
# outcomes; the diverged seed sets are asserted explicitly below.
HEURISTIC_ATTACK_FIDELITY_GOLDEN: _Golden = {
    **HEURISTIC_C2_GOLDEN,
    ("heuristic", 1): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 2): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 67)),
    ),
    ("heuristic", 4): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 46)),
    ),
    ("heuristic", 5): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 8): (
        "player_0",
        "one_player_remaining",
        (("player_0", 12), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 10): (
        "player_0",
        "one_player_remaining",
        (("player_0", 53), ("player_1", 0), ("player_2", 0)),
    ),
    ("heuristic", 12): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 26)),
    ),
}
HEURISTIC_FOUR_PLAYER_ATTACK_FIDELITY_GOLDEN: _Golden = {
    **HEURISTIC_FOUR_PLAYER_GOLDEN,
    ("heuristic", 2): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 4), ("player_3", 0)),
    ),
    ("heuristic", 3): (
        "player_0",
        "one_player_remaining",
        (("player_0", 21), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 5): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 6): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 42), ("player_3", 0)),
    ),
    ("heuristic", 7): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 9): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 33), ("player_3", 0)),
    ),
    ("heuristic", 10): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 11): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 14), ("player_3", 0)),
    ),
}


def _outcome(agent: str, seed: int, players: int = 3) -> tuple:
    r = run_simulation(SimulationConfig("table", players, seed, agent, max_turns=80))
    return (
        r["winner"],
        r["termination_reason"],
        tuple(sorted(r["final_populations"].items())),
    )


def test_heuristic_table_outcomes_match_attack_fidelity_golden() -> None:
    for seed in range(1, 13):
        assert (
            _outcome("heuristic", seed)
            == HEURISTIC_ATTACK_FIDELITY_GOLDEN[("heuristic", seed)]
        )


def test_heuristic_four_player_outcomes_match_attack_fidelity_golden() -> None:
    for seed in range(1, 13):
        assert (
            _outcome("heuristic", seed, players=4)
            == (HEURISTIC_FOUR_PLAYER_ATTACK_FIDELITY_GOLDEN[("heuristic", seed)])
        )


def test_heuristic_outcomes_intentionally_diverged_after_attack_fidelity() -> None:
    # C-stage divergence assertion (C2 precedent): exactly these seeds changed
    # when the attack/retaliation model bugs were removed.
    changed_3p = [
        seed
        for seed in range(1, 13)
        if _outcome("heuristic", seed) != HEURISTIC_C2_GOLDEN[("heuristic", seed)]
    ]
    changed_4p = [
        seed
        for seed in range(1, 13)
        if _outcome("heuristic", seed, players=4)
        != HEURISTIC_FOUR_PLAYER_GOLDEN[("heuristic", seed)]
    ]
    assert changed_3p == [1, 2, 4, 5, 8, 10, 12]
    assert changed_4p == [2, 3, 5, 6, 7, 9, 10, 11]


def test_heuristic_final_strike_chain_seed_16_matches_attack_fidelity_golden() -> None:
    # Re-pinned after the attack/retaliation fidelity fixes: the wider
    # final-retaliation pool turns seed 16 into a mutual annihilation.
    assert _outcome("heuristic", 16) == (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0)),
    )


def test_heuristic_table_outcomes_intentionally_diverged_after_c2() -> None:
    changed = [
        seed
        for _, seed in HEURISTIC_PRE_C2_CHANGED
        if _outcome("heuristic", seed) != HEURISTIC_PRE_C2_CHANGED[("heuristic", seed)]
    ]
    # Seed 16 dropped out of this list on 2026-07-02: the attack/retaliation
    # fidelity fixes coincidentally land seed 16 back on its pre-C2 outcome
    # (both are total mutual annihilation).
    assert changed == [5, 6, 8, 10]


def test_random_table_outcomes_deterministic() -> None:
    for seed in range(1, 13):
        assert _outcome("random", seed) == _outcome("random", seed)


def test_random_table_outcomes_diverged_from_a0() -> None:
    # A2 makes RandomAgent draw RNG to pick secret/propaganda targets, so at least
    # one random game now differs from the pre-A2 (A0) golden. This documents the
    # intentional behavior change while heuristic stays pinned.
    changed = [
        seed
        for seed in range(1, 13)
        if _outcome("random", seed) != RANDOM_A0_GOLDEN[("random", seed)]
    ]
    assert changed, "expected at least one random game to diverge after A2"


def test_random_table_outcomes_diverged_after_setup_peace_fidelity() -> None:
    # The 2026-07-02 setup/peace fidelity pass makes RandomAgent draw RNG for the
    # opening SETUP_PLACE commitments and any peace-restoration STRATEGY_REPLACE
    # window, so random outcomes intentionally diverge from the pre-change golden
    # while heuristic outcomes stay pinned (options[0] preserves legacy behavior).
    changed = [
        seed
        for seed in range(1, 13)
        if _outcome("random", seed) != RANDOM_PRE_SETUP_PEACE_GOLDEN[("random", seed)]
    ]
    assert changed, "expected random games to diverge after the setup/peace pass"
