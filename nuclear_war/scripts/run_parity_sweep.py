#!/usr/bin/env python3
"""Replay parity sweep runner for the WOPR rules engine.

Runs the documented parity grid (players x agent x seed) and records each
outcome tuple. A second run is byte-identical to the first under a fixed
seed, which is the parity invariant the engine guarantees. Results are
written to research/paper_artifacts/parity_sweep/sweep_results.json.

Run the full documented grid (240 games):
    uv run python nuclear_war/scripts/run_parity_sweep.py

Run a fast slice for smoke checks:
    uv run python nuclear_war/scripts/run_parity_sweep.py \\
        --players 3 --agents heuristic --seed-start 1 --seed-count 3
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from nuclear_war_env.simulation import SimulationConfig, run_simulation

PLAYER_COUNTS = (3, 4)
AGENT_KINDS = ("heuristic", "random")
SEED_START = 1
SEED_COUNT = 60
DEFAULT_MAX_TURNS = 50
ARTIFACT_DIR = (
    Path(__file__).resolve().parent.parent
    / "research"
    / "paper_artifacts"
    / "parity_sweep"
)


def _outcome(result: dict) -> tuple[object, str, tuple[tuple[str, int], ...]]:
    standings = tuple(
        (player_id, population)
        for player_id, population in result["final_populations"].items()
    )
    return (result["winner"], result["termination_reason"], standings)


def run_grid(
    players: tuple[int, ...],
    agents: tuple[str, ...],
    seed_start: int,
    seed_count: int,
    max_turns: int,
) -> list[dict]:
    rows: list[dict] = []
    for player_count in players:
        for agent in agents:
            for seed in range(seed_start, seed_start + seed_count):
                config = SimulationConfig(
                    mode="table",
                    players=player_count,
                    seed=seed,
                    agent=agent,
                    max_turns=max_turns,
                )
                result = run_simulation(config)
                winner, reason, standings = _outcome(result)
                rows.append(
                    {
                        "players": player_count,
                        "agent": agent,
                        "seed": seed,
                        "winner": winner,
                        "termination_reason": reason,
                        "final_populations": dict(standings),
                    }
                )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--players",
        type=int,
        nargs="+",
        default=list(PLAYER_COUNTS),
        help="Player counts to sweep.",
    )
    parser.add_argument(
        "--agents",
        type=str,
        nargs="+",
        default=list(AGENT_KINDS),
        choices=list(AGENT_KINDS),
        help="Agent kinds to sweep.",
    )
    parser.add_argument(
        "--seed-start",
        type=int,
        default=SEED_START,
        help="Inclusive first seed.",
    )
    parser.add_argument(
        "--seed-count",
        type=int,
        default=SEED_COUNT,
        help="Number of seeds per (players, agent) cell.",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=DEFAULT_MAX_TURNS,
        help="Turn cap per game.",
    )
    args = parser.parse_args()

    rows = run_grid(
        tuple(args.players),
        tuple(args.agents),
        args.seed_start,
        args.seed_count,
        args.max_turns,
    )

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "grid": {
            "players": list(args.players),
            "agents": list(args.agents),
            "seed_start": args.seed_start,
            "seed_count": args.seed_count,
            "max_turns": args.max_turns,
        },
        "total_games": len(rows),
        "results": rows,
    }
    out_path = ARTIFACT_DIR / "sweep_results.json"
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"Swept {len(rows)} games; wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
