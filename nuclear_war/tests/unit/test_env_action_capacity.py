"""PettingZoo action adapter capacity tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.env_utils import action_mask, select_action


def test_env_action_adapter_exposes_more_than_sixteen_actions() -> None:
    actions = [
        build_action("p1", ActionType.PASS, f"Action {index}", {"slot": index})
        for index in range(17)
    ]

    mask = action_mask(actions)
    selected = select_action(actions, 16)

    assert int(mask.sum()) == 17
    assert selected.payload == {"slot": 16}


@pytest.mark.parametrize("index", [-1, 2, 256])
def test_env_action_adapter_rejects_masked_action_index(index: int) -> None:
    actions = [
        build_action("p1", ActionType.PASS, f"Action {slot}", {"slot": slot})
        for slot in range(2)
    ]

    with pytest.raises(ValueError, match=f"Invalid action index {index}"):
        select_action(actions, index)
