"""Focused PettingZoo v1 behavior tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.factory import create_table_env


def test_table_env_rejects_masked_action_index() -> None:
    env = create_table_env(seed=1)
    env.reset()
    observation, *_ = env.last()
    assert isinstance(observation, dict)
    invalid_action = _first_masked_action(observation["action_mask"])

    with pytest.raises(ValueError, match="Invalid action index"):
        env.step(invalid_action)


def _first_masked_action(mask) -> int:
    return next(index for index, value in enumerate(mask) if int(value) == 0)
