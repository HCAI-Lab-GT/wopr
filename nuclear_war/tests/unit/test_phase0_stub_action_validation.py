"""Phase 0 stub action validation tests."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_env.env_stub_aec import Phase0AECEnv
from nuclear_war_env.env_stub_parallel import Phase0ParallelEnv


def test_phase0_aec_rejects_string_action() -> None:
    malformed_action: Any = "1"
    env = Phase0AECEnv(seed=1)

    with pytest.raises(ValueError, match="Action must be an integer"):
        env.step(malformed_action)


def test_phase0_parallel_rejects_boolean_action() -> None:
    malformed_action: Any = True
    env = Phase0ParallelEnv(seed=1)
    env.reset()

    with pytest.raises(ValueError, match="Action must be an integer"):
        env.step({"player_0": malformed_action, "player_1": 0})
