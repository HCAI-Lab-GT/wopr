"""Environment action-index validation tests."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.env_postal import PostalParallelEnv
from nuclear_war_env.env_table import TableAECEnv
from nuclear_war_env.env_utils import select_action


def test_select_action_rejects_boolean_index() -> None:
    actions = [
        build_action("p1", ActionType.PASS, "Pass"),
        build_action("p1", ActionType.DRAW, "Draw"),
    ]
    malformed_action: Any = True

    with pytest.raises(ValueError, match="Action index must be an integer"):
        select_action(actions, malformed_action)


def test_select_action_accepts_numpy_integer_index() -> None:
    actions = [
        build_action("p1", ActionType.PASS, "Pass"),
        build_action("p1", ActionType.DRAW, "Draw"),
    ]

    selected = select_action(actions, np.int64(1))

    assert selected.action_type is ActionType.DRAW


def test_table_env_rejects_string_action_index() -> None:
    malformed_action: Any = "0"
    env = TableAECEnv(seed=1)

    with pytest.raises(ValueError, match="Action index must be an integer"):
        env.step(malformed_action)


def test_postal_env_rejects_boolean_action_index() -> None:
    malformed_action: Any = True
    env = PostalParallelEnv(seed=1)
    env.reset()

    with pytest.raises(ValueError, match="Action index must be an integer"):
        env.step({"player_0": malformed_action, "player_1": 0})
