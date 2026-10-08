"""Postal Radioactive Fallout die parity and postal-sweep outcome goldens.

C-stage fidelity fix (2026-07-03): four postal equipment resolutions moved from
the two-d10 fallout spinner to the 6-sided Radioactive Fallout die (space
platform launch, cruise launch, killer satellite attack, MX per-segment rolls).

Two goldens guard the change:

1. Scenario divergence golden. The affected equipment is expansion-only and is
   NOT in the default postal deck, so full seeded sweep games never launch it
   (see ``test_postal_sweep_outcomes_match_golden``). The divergence
   is therefore pinned at the scenario level with directly-injected orders. Each
   scenario's pre-change outcome (``_PRE_D6``) and post-change outcome (``_D6``)
   were captured from HEAD 127c9de and the fix respectively; the divergence is
   asserted explicitly. Seed 2 flips every single-roll launch because the old
   spinner rolled a dud (05-09, launched under the old code) where the die now
   rolls a nuclear cloud.

2. Postal-sweep golden. Default-agent postal games stay byte-identical under the
   fallout-die substitution alone, mirroring the table-mode byte-identity gate —
   the equipment involved is unreachable by default-deck games. However, a
   *separate* 2026-07-04 fix (pure-engine final-strike targeting; see
   ``phase_final_strike`` / ``_assign_pure_engine_final_strike_targets`` in
   ``engine/postal/handlers_early.py``) changed default postal outcomes: it
   makes phase-3 final strikes actually fire when a pooled retaliation order
   was hand-assembled with no target, instead of being silently dropped by
   ``execute_launches``. That re-baselined 7 of the 24 tuples below (all in the
   ``random``-agent games). The fallout-die byte-identity claim above still
   holds in isolation; the die substitution did not move these outcomes, the
   final-strike-targeting fix did.
"""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.engine.launch import execute_launches
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.simulation import SimulationConfig, run_simulation
from nuclear_war_env.state import GameState, Ruleset, create_players

_ROLL_EVENTS = {"spinner_result", "fallout_die_result"}


def _postal(seed: int) -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=seed)
    state.population_bank = [10, 5]
    return state


def _rolls(events: list) -> tuple[str, ...]:
    return tuple(e.event_type for e in events if e.event_type in _ROLL_EVENTS)


def _outcomes(events: list) -> tuple[str, ...]:
    return tuple(
        e.event_type
        for e in events
        if e.event_type not in _ROLL_EVENTS and e.event_type != "phase_complete"
    )


def _space_platform_seed2() -> dict:
    state = _postal(2)
    state.players["p1"].pending_orders["space_platform_launch"] = [
        {"platform": "platform1", "warheads": [10]}
    ]
    events = execute_postal_turn(state)
    return {
        "rolls": _rolls(events),
        "outcomes": _outcomes(events),
        "owner_pop": sum(state.players["p1"].population),
        "platform_present": "platform1"
        in state.players["p1"].pending_orders.get("space_platforms", {}),
    }


def _cruise_seed2() -> dict:
    state = _postal(2)
    state.players["p1"].pending_orders["cruise_launch"] = [
        {"missile": "cruise1", "target": "p2", "yield": 10}
    ]
    events = execute_postal_turn(state)
    return {
        "rolls": _rolls(events),
        "outcomes": _outcomes(events),
        "missile_present": "cruise1"
        in state.players["p1"].pending_orders.get("cruise_missiles", {}),
    }


def _killer_satellite_seed2() -> dict:
    state = _postal(2)
    state.players["p1"].pending_orders["killer_satellites"] = {
        "sat1": {"status": "orbit"}
    }
    state.players["p2"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10]}
    }
    state.players["p1"].pending_orders["killer_satellite_attack"] = [
        {"satellite": "sat1", "target_player": "p2", "platform": "platform1"}
    ]
    events = execute_postal_turn(state)
    return {
        "rolls": _rolls(events),
        "outcomes": _outcomes(events),
        "platform_survives": "platform1"
        in state.players["p2"].pending_orders.get("space_platforms", {}),
    }


def _mx_seed41() -> dict:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards(
        [
            Card(
                "mx",
                CardCategory.DELIVERY,
                "MX Missile",
                metadata={"postal_effect": "mx_missile", "capacity": 1},
            ),
            Card("large", CardCategory.WARHEAD, "20 Mt", value=20),
        ]
    )
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.rng = SeededRNG(seed=41)
    state.players["p1"].pending_orders["launches"] = {
        "mx": {"delivery": "mx", "warheads": ["large"], "target": "p2"}
    }
    events = execute_launches(state)
    return {
        "rolls": _rolls(events),
        "yields": tuple(
            e.payload["yield"] for e in events if e.event_type == "warhead_detonated"
        ),
        "target_pop": sum(state.players["p2"].population),
    }


_SCENARIOS = {
    "space_platform": _space_platform_seed2,
    "cruise": _cruise_seed2,
    "killer_satellite": _killer_satellite_seed2,
    "mx": _mx_seed41,
}

# Pre-change outcomes captured from HEAD 127c9de (two-d10 spinner).
_PRE_D6 = {
    "space_platform": {
        "rolls": ("spinner_result",),
        "outcomes": ("space_platform_launched",),
        "owner_pop": 30,
        "platform_present": True,
    },
    "cruise": {
        "rolls": ("spinner_result",),
        "outcomes": ("cruise_launched",),
        "missile_present": True,
    },
    "killer_satellite": {
        "rolls": ("spinner_result",),
        "outcomes": ("killer_satellite_destroyed_platform",),
        "platform_survives": False,
    },
    "mx": {
        "rolls": ("spinner_result", "spinner_result"),
        "yields": (2, 2),
        "target_pop": 26,
    },
}

# Post-change outcomes with the 6-sided Radioactive Fallout die.
_D6 = {
    "space_platform": {
        "rolls": ("fallout_die_result", "fallout_die_result"),
        "outcomes": ("space_platform_crashed",),
        "owner_pop": 20,
        "platform_present": False,
    },
    "cruise": {
        "rolls": ("fallout_die_result",),
        "outcomes": ("cruise_launch_failed",),
        "missile_present": False,
    },
    "killer_satellite": {
        "rolls": ("fallout_die_result",),
        "outcomes": ("killer_satellite_failed",),
        "platform_survives": True,
    },
    "mx": {
        "rolls": ("fallout_die_result", "fallout_die_result"),
        "yields": (6, 5),
        "target_pop": 19,
    },
}


def test_postal_equipment_scenarios_match_fallout_die_golden() -> None:
    for name, scenario in _SCENARIOS.items():
        assert scenario() == _D6[name], name


def test_postal_equipment_scenarios_intentionally_diverged_from_spinner() -> None:
    # Every affected mechanic changes its seeded outcome under the die.
    diverged = [
        name for name, scenario in _SCENARIOS.items() if scenario() != _PRE_D6[name]
    ]
    assert diverged == ["space_platform", "cruise", "killer_satellite", "mx"]


# Postal sweep outcomes. Originally captured from HEAD 127c9de to prove the
# fallout-die substitution is byte-identical for default-agent games (the
# affected equipment is expansion-only and never enters the default deck, so
# the die swap alone cannot change any default-agent game — that claim still
# holds). Re-baselined 2026-07-04: the pure-engine final-strike-targeting fix
# (phase_final_strike now assigns a deterministic target to still-untargeted
# pooled retaliation orders before run_final_strike consumes them, instead of
# letting execute_launches silently drop them) changed 7 of the 24 tuples
# below, all in the `random`-agent games. This is an intentional outcome
# change (Issue 2 fix), not a regression.
_PostalGolden = dict[
    tuple[str, int, int], tuple[object, str, tuple[tuple[str, int], ...]]
]
POSTAL_SWEEP_UNCHANGED_GOLDEN: _PostalGolden = {
    ("heuristic", 1, 3): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 23)),
    ),
    ("heuristic", 2, 3): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 101)),
    ),
    ("heuristic", 3, 3): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 50)),
    ),
    ("heuristic", 4, 3): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 16)),
    ),
    ("heuristic", 5, 3): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 99)),
    ),
    ("heuristic", 6, 3): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 14)),
    ),
    ("random", 1, 3): (
        "player_0",
        "one_player_remaining",
        (("player_0", 44), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 2, 3): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 76)),
    ),
    ("random", 3, 3): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 63), ("player_2", 0)),
    ),
    ("random", 4, 3): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 43)),
    ),
    ("random", 5, 3): (
        "player_0",
        "one_player_remaining",
        (("player_0", 45), ("player_1", 0), ("player_2", 0)),
    ),
    ("random", 6, 3): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 21)),
    ),
    ("heuristic", 1, 4): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 57), ("player_2", 0), ("player_3", 0)),
    ),
    ("heuristic", 2, 4): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 72), ("player_3", 0)),
    ),
    ("heuristic", 3, 4): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 12), ("player_3", 0)),
    ),
    ("heuristic", 4, 4): (
        "player_3",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 116)),
    ),
    ("heuristic", 5, 4): (
        "player_3",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 21)),
    ),
    ("heuristic", 6, 4): (
        "player_3",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 52)),
    ),
    ("random", 1, 4): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 31), ("player_2", 0), ("player_3", 0)),
    ),
    ("random", 2, 4): (
        "player_2",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 31), ("player_3", 0)),
    ),
    ("random", 3, 4): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 104), ("player_2", 0), ("player_3", 0)),
    ),
    ("random", 4, 4): (
        None,
        "no_players_remaining",
        (("player_0", 0), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("random", 5, 4): (
        "player_0",
        "one_player_remaining",
        (("player_0", 52), ("player_1", 0), ("player_2", 0), ("player_3", 0)),
    ),
    ("random", 6, 4): (
        "player_1",
        "one_player_remaining",
        (("player_0", 0), ("player_1", 51), ("player_2", 0), ("player_3", 0)),
    ),
}


def _postal_outcome(agent: str, seed: int, players: int) -> tuple:
    result = run_simulation(
        SimulationConfig("postal", players, seed, agent, max_turns=120)
    )
    return (
        result["winner"],
        result["termination_reason"],
        tuple(sorted(result["final_populations"].items())),
    )


def test_postal_sweep_outcomes_match_golden() -> None:
    for (agent, seed, players), expected in POSTAL_SWEEP_UNCHANGED_GOLDEN.items():
        assert _postal_outcome(agent, seed, players) == expected, (agent, seed, players)
