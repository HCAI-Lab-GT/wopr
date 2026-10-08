"""Table-mode secret / top-secret resolution.

The rules resolve a Secret the moment it is drawn. Table mode has no separate
target-selection step (postal handles that via player-chosen ``secret_targets``
orders), so V1 uses a deterministic target policy: gains go to the drawer and every
offensive secret targets the highest-population living opponent.

Roadmap: ``select_secret_target`` is the seam to swap this deterministic policy for
a legal-action targeting choice (mirroring the postal flow) so agents pick targets.
"""

from __future__ import annotations

from collections.abc import Callable

from nuclear_war_env.cards import Card
from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.state import GameState

# ``apply_secret_effect`` is mode-agnostic despite living under ``postal``.
from .postal.secret_effects import apply_secret_effect
from .target_policy import highest_population_opponent

SecretTargetSelector = Callable[[GameState, str, Card], "str | None"]


def select_secret_target(
    state: GameState,
    drawer_id: str,
    card: Card,
) -> str | None:
    """Deterministic V1 target policy for table-mode secret resolution."""
    metadata = card.metadata if isinstance(card.metadata, dict) else {}
    if _as_int(metadata.get("gain_from_bank_millions")) > 0:
        return drawer_id
    return highest_population_opponent(state, drawer_id)


def resolve_secrets(
    state: GameState,
    player_id: str,
    select_target: SecretTargetSelector = select_secret_target,
) -> list[EngineEvent]:
    """Resolve every secret currently queued for ``player_id`` and clear them."""
    events: list[EngineEvent] = []
    player = state.players[player_id]
    # Resolving a secret can trigger a chain (e.g. the target's retaliation) that
    # eliminates the drawer mid-turn; a dead drawer resolves no further secrets.
    while player.secrets and player.alive:
        secret_id = player.secrets[0]
        card = state.card_by_id(secret_id)
        target_id = select_target(state, player_id, card)
        if target_id is None or target_id not in state.players:
            # An offensive secret with no living opponent is a legitimate no-op:
            # the card is already discarded, so nothing changes and nothing logs.
            player.secrets.pop(0)
            continue
        events.extend(apply_secret_effect(state, player_id, secret_id, target_id))
        if secret_id in player.secrets:
            player.secrets.remove(secret_id)
    return events


def is_self_secret(card: Card) -> bool:
    """A secret that only benefits the drawer (gain-from-bank) targets self.

    Mirrors select_secret_target's gain branch: such a secret auto-resolves to the
    drawer with no agent decision; every other secret is offensive (a SECRET_TARGET
    decision).
    """
    metadata = card.metadata if isinstance(card.metadata, dict) else {}
    return _as_int(metadata.get("gain_from_bank_millions")) > 0


def _as_int(value: object) -> int:
    return value if type(value) is int else 0


__all__ = [
    "select_secret_target",
    "resolve_secrets",
    "is_self_secret",
    "SecretTargetSelector",
]
