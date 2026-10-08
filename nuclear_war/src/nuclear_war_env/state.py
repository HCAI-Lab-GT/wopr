"""State management for the core Nuclear War rules engine."""

from __future__ import annotations

from collections import OrderedDict, deque
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

from .cards import Card
from .population import distribute_population
from .rng import SeededRNG
from .variants import ACTIVE_VARIANT_ID

if TYPE_CHECKING:
    from .engine.decision import DecisionCursor

HAND_LIMIT = 10
FACE_DOWN_SLOTS = 2
DETERRENT_SLOTS = 2


class Ruleset(StrEnum):
    TABLE = "table"
    POSTAL = "postal"


@dataclass
class PlayerState:
    """Tracks per-player information shared by table and postal modes."""

    player_id: str
    population: list[int]
    hand: list[str] = field(default_factory=list)
    deterrents: list[str | None] = field(
        default_factory=lambda: [None] * DETERRENT_SLOTS
    )
    face_up: str | None = None
    face_down_queue: deque[str | None] = field(
        default_factory=lambda: deque(
            [None] * FACE_DOWN_SLOTS,
            maxlen=FACE_DOWN_SLOTS,
        )
    )
    secrets: list[str] = field(default_factory=list)
    final_strike_cards: list[str] = field(default_factory=list)
    pending_orders: dict[str, Any] = field(default_factory=dict)
    alive: bool = True
    at_war: bool = False

    def enqueue_face_down(self, card_id: str | None) -> None:
        self.face_down_queue.append(card_id)

    def advance_face_down(self) -> None:
        self.face_up = self.face_down_queue.popleft()
        self.face_down_queue.append(None)

    def remove_population(self, amount: int) -> int:
        total = sum(self.population)
        loss = min(total, amount)
        remaining = total - loss
        self.population = distribute_population(remaining)
        if remaining == 0:
            self.alive = False
        return loss

    def add_population(self, amount: int) -> None:
        total = sum(self.population) + amount
        self.population = distribute_population(total)

    def draw_from(self, card: Card) -> None:
        if len(self.hand) >= HAND_LIMIT:
            raise ValueError("Hand is already at limit")
        self.hand.append(card.identifier)

    def discard_from_hand(self, card_id: str) -> None:
        self.hand.remove(card_id)


@dataclass
class GameState:
    """Global game container for deterministic engine operations."""

    ruleset: Ruleset
    players: OrderedDict[str, PlayerState]
    draw_pile: list[Card]
    discard_pile: list[Card] = field(default_factory=list)
    population_bank: list[int] = field(default_factory=list)
    card_lookup: dict[str, Card] = field(default_factory=dict)
    rng: SeededRNG = field(default_factory=SeededRNG)
    turn: int = 0
    war_log: list[str] = field(default_factory=list)
    peace: bool = True
    press_enabled: bool = False
    variant_id: str = ACTIVE_VARIANT_ID
    next_player_id: str | None = None
    current_player_id: str | None = None
    cursor: DecisionCursor | None = None

    def alive_players(self) -> list[PlayerState]:
        return [player for player in self.players.values() if player.alive]

    def draw_card(self) -> Card:
        if not self.draw_pile:
            if not self.discard_pile:
                raise ValueError("Cannot draw from empty deck")
            self.draw_pile = self.rng.shuffle(self.discard_pile)
            self.discard_pile = []
        return self.draw_pile.pop(0)

    def discard(self, card: Card) -> None:
        self.discard_pile.append(card)

    def next_turn(self) -> None:
        self.turn += 1

    def register_cards(self, cards: Iterable[Card]) -> None:
        for card in cards:
            if card.identifier in self.card_lookup:
                raise ValueError(f"Duplicate card identifier: {card.identifier}")
            self.card_lookup[card.identifier] = card

    def card_by_id(self, card_id: str) -> Card:
        try:
            return self.card_lookup[card_id]
        except KeyError as exc:  # pragma: no cover - defensive
            raise KeyError(f"Unknown card identifier: {card_id}") from exc


def create_players(
    player_ids: Iterable[str],
    starting_population: int,
) -> OrderedDict[str, PlayerState]:
    population_cards = distribute_population(starting_population)
    return OrderedDict(
        (player_id, PlayerState(player_id=player_id, population=list(population_cards)))
        for player_id in player_ids
    )


__all__ = [
    "PlayerState",
    "GameState",
    "Ruleset",
    "HAND_LIMIT",
    "FACE_DOWN_SLOTS",
    "DETERRENT_SLOTS",
    "distribute_population",
    "create_players",
]
