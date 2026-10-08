"""Shared helpers for PettingZoo environments."""

from __future__ import annotations

from numbers import Integral
from typing import Any

import numpy as np
from gymnasium import spaces

from .actions import LegalAction, legal_actions
from .observation import to_numeric_observation
from .state import GameState

MAX_ACTIONS = 256
OBSERVATION_SIZE = 6


def action_space() -> spaces.Discrete:
    return spaces.Discrete(MAX_ACTIONS)


def observation_space() -> spaces.Dict:
    return spaces.Dict(
        {
            "observation": spaces.Box(
                low=0.0,
                high=1_000_000.0,
                shape=(OBSERVATION_SIZE,),
                dtype=np.float32,
            ),
            "action_mask": spaces.Box(
                low=0,
                high=1,
                shape=(MAX_ACTIONS,),
                dtype=np.int8,
            ),
        }
    )


def env_observation(
    state: GameState, player_id: str, mode: str
) -> dict[str, np.ndarray]:
    actions = legal_actions(state, player_id, mode)
    return {
        "observation": np.array(
            to_numeric_observation(state, player_id),
            dtype=np.float32,
        ),
        "action_mask": action_mask(actions),
    }


def _check_action_capacity(actions: list[LegalAction]) -> list[LegalAction]:
    if len(actions) > MAX_ACTIONS:
        raise ValueError(
            f"Legal action count {len(actions)} exceeds the discrete action "
            f"space size {MAX_ACTIONS}; raise MAX_ACTIONS"
        )
    return actions


def action_mask(actions: list[LegalAction]) -> np.ndarray:
    mask = np.zeros(MAX_ACTIONS, dtype=np.int8)
    for index, _action in enumerate(_check_action_capacity(actions)):
        mask[index] = 1
    return mask


def select_action(actions: list[LegalAction], index: Any) -> LegalAction:
    if isinstance(index, bool) or not isinstance(index, Integral):
        raise ValueError("Action index must be an integer")
    action_index = int(index)
    visible_actions = _check_action_capacity(actions)
    if 0 <= action_index < len(visible_actions):
        return visible_actions[action_index]
    if not visible_actions:
        raise ValueError("No legal actions available")
    raise ValueError(
        f"Invalid action index {action_index}; "
        f"legal range is 0..{len(visible_actions) - 1}"
    )


__all__ = [
    "MAX_ACTIONS",
    "action_space",
    "observation_space",
    "env_observation",
    "select_action",
]
