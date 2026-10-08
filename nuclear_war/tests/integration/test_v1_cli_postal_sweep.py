"""Postal CLI replay sweep regressions."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("players", "agent", "seed"),
    [(3, "random", 6), (3, "heuristic", 7)],
)
def test_postal_cli_known_replay_failures_are_valid(
    players: int,
    agent: str,
    seed: int,
    tmp_path: Path,
) -> None:
    out = tmp_path / f"postal-{players}-{agent}-{seed}.json"
    result = subprocess.run(
        [
            "uv",
            "run",
            "nuclear-war",
            "simulate",
            "--mode",
            "postal",
            "--players",
            str(players),
            "--seed",
            str(seed),
            "--agent",
            agent,
            "--max-turns",
            "120",
            "--out",
            str(out),
        ],
        cwd=Path(__file__).parents[2],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
