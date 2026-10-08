"""Test configuration for Nuclear War Phase 0 suite."""

from __future__ import annotations

import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from nuclear_war_concordia.c2_artifacts import build_c2_artifact  # noqa: E402
from nuclear_war_concordia.config import load_concordia_no_press_config  # noqa: E402
from nuclear_war_concordia.harness_agents import build_seat_runtimes  # noqa: E402
from nuclear_war_concordia.harness_seat_runtime import (  # noqa: E402
    ConcordiaSeatRuntime,
)
from nuclear_war_env.simulation import (  # noqa: E402
    SimulationConfig,
    run_table_simulation_with_decision_agents,
)

C2RuntimeCase = tuple[dict[str, Any], dict[str, ConcordiaSeatRuntime]]


@pytest.fixture
def authority_config_payload() -> dict[str, object]:
    seats = {
        f"player_{index}": {
            "agent": "concordia_first_legal",
            "identity": {
                "name": f"Commander {index}",
                "role": "strategic actor",
            },
        }
        for index in range(4)
    }
    seats["player_0"]["authority"] = {
        "archetype": "sole_authority",
        "parameters": {"deference": 0.0},
        "spokesperson": "executive",
        "members": [
            {
                "member_id": member_id,
                "identity": {"name": name, "role": role},
            }
            for member_id, name, role in (
                ("executive", "Executive", "final decision authority"),
                ("strategic_advisor", "Strategic Advisor", "strategic advice"),
                ("risk_advisor", "Risk Advisor", "risk advice"),
            )
        ],
    }
    return {
        "players": 4,
        "seed": 51,
        "max_turns": 10,
        "runtime": "auto",
        "seats": seats,
    }


def _run_c2_case(payload: dict[str, object]) -> C2RuntimeCase:
    payload["max_turns"] = 2
    config = load_concordia_no_press_config(payload)
    runtimes = build_seat_runtimes(config, [], "fallback")
    replay = run_table_simulation_with_decision_agents(
        SimulationConfig(
            mode="table",
            players=config.players,
            seed=config.seed,
            agent="mixed_seats",
            max_turns=config.max_turns,
            variant_id=config.variant_id,
        ),
        {player_id: runtime.strategic_agent for player_id, runtime in runtimes.items()},
    )
    return replay, runtimes


@pytest.fixture
def c2_artifact_factory() -> Callable[
    [dict[str, object]], tuple[dict[str, Any], dict[str, Any]]
]:
    def build(payload: dict[str, object]) -> tuple[dict[str, Any], dict[str, Any]]:
        replay, runtimes = _run_c2_case(payload)
        return replay, build_c2_artifact(replay, runtimes)

    return build


@pytest.fixture
def c2_runtime_case(
    authority_config_payload: dict[str, object],
) -> C2RuntimeCase:
    return _run_c2_case(authority_config_payload)


@pytest.fixture
def c2_artifact_case(
    authority_config_payload: dict[str, object],
    c2_artifact_factory: Callable[
        [dict[str, object]], tuple[dict[str, Any], dict[str, Any]]
    ],
) -> tuple[dict[str, Any], dict[str, Any]]:
    return c2_artifact_factory(authority_config_payload)
