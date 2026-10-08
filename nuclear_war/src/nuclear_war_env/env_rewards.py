"""Terminal win/loss reward scheme shared by both PettingZoo environments.

Scheme (interface layer only — the engine itself is reward-free):

- ``+1.0`` to each surviving player at the step the game ends
  (``engine.terminal.game_over``),
- ``-1.0`` to a player at the step its elimination becomes final (dead with
  no final-strike retaliation left),
- ``0.0`` for every other step, including truncation at ``max_cycles``.

The LLM decision harness drives the engine through the decision loop and
ignores these rewards; they exist so RL-style consumers of the PettingZoo
API can distinguish a winner from the eliminated players.
"""

from __future__ import annotations

from .state import PlayerState


def terminal_reward(player: PlayerState, done: bool) -> float:
    """Reward for an agent at the step it becomes terminated."""
    if not player.alive:
        return -1.0
    return 1.0 if done else 0.0


__all__ = ["terminal_reward"]
