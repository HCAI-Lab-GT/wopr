"""Simulation turn-order integration tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.action_models import ActionType, LegalAction
from nuclear_war_env.simulation import SimulationConfig, run_simulation

# Note: the simulation-level anti-missile turn-order jump is verified directly on
# the turn generator in tests/unit/test_turn_player_ids.py. With the faithful
# turn driver a skipped (action-less) player is invisible in the action log, so the
# no-skip / no-duplicate invariant is asserted on turn_player_ids instead of here.


class IllegalAgent:
    def choose(self, _actions: list[LegalAction]) -> LegalAction:
        return LegalAction("ghost:pass", "ghost", ActionType.PASS, "Illegal")


def test_simulation_rejects_agent_action_outside_legal_actions(monkeypatch) -> None:
    monkeypatch.setattr(
        "nuclear_war_env.simulation._build_agent",
        lambda _agent, _rng: IllegalAgent(),
    )
    config = SimulationConfig(
        mode="table",
        players=2,
        seed=1,
        agent="heuristic",
        max_turns=1,
    )

    with pytest.raises(ValueError, match="Agent selected illegal action"):
        run_simulation(config)
