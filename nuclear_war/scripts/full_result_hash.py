#!/usr/bin/env python3
"""Full-result parity hash (incl. event log) for the postal/table sweeps.

Hashes the complete per-game result dict (winner, populations, actions, events,
...) across players {3,4} x agents {heuristic,random} x seeds, per mode. Used as
the byte-identity / re-baseline gate:

    uv run python scripts/full_result_hash.py                  # full 240/mode
    uv run python scripts/full_result_hash.py --seed-count 20  # fast slice
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from nuclear_war_env.simulation import SimulationConfig, run_simulation

PLAYER_COUNTS = (3, 4)
AGENT_KINDS = ("heuristic", "random")
MODES = ("table", "postal")
ARTIFACT = (
    Path(__file__).resolve().parent.parent
    / "research"
    / "paper_artifacts"
    / "parity_sweep"
    / "full_result_hashes.json"
)


def mode_hash(mode: str, seed_start: int, seed_count: int, max_turns: int) -> str:
    digest = hashlib.sha256()
    for players in PLAYER_COUNTS:
        for agent in AGENT_KINDS:
            for seed in range(seed_start, seed_start + seed_count):
                result = run_simulation(
                    SimulationConfig(
                        mode=mode,
                        players=players,
                        seed=seed,
                        agent=agent,
                        max_turns=max_turns,
                    )
                )
                digest.update(
                    json.dumps(result, sort_keys=True, default=str).encode("utf-8")
                )
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-start", type=int, default=1)
    parser.add_argument("--seed-count", type=int, default=60)
    parser.add_argument("--max-turns", type=int, default=50)
    parser.add_argument("--out", type=str, default=str(ARTIFACT))
    args = parser.parse_args()

    hashes = {
        mode: mode_hash(mode, args.seed_start, args.seed_count, args.max_turns)
        for mode in MODES
    }
    for mode in MODES:
        print(f"{mode} {hashes[mode]}")
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(
            {
                "seed_start": args.seed_start,
                "seed_count": args.seed_count,
                "max_turns": args.max_turns,
                "hashes": hashes,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
