"""Seeded random number utilities for deterministic engine behavior."""

from __future__ import annotations

import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import TypeVar

from .integer_validation import is_strict_int

T = TypeVar("T")


@dataclass
class SeededRNG:
    """Wrapper around ``random.Random`` that exposes deterministic helpers."""

    seed: int | None = None
    _random: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        validate_seed(self.seed)
        self._random = random.Random(self.seed)

    def shuffle(self, items: Sequence[T]) -> list[T]:
        data = list(items)
        self._random.shuffle(data)
        return data

    def choose(self, items: Sequence[T]) -> T:
        if not items:
            raise ValueError("Cannot choose from an empty sequence")
        return items[self._random.randrange(len(items))]

    def randint(self, lower: int, upper: int) -> int:
        if not is_strict_int(lower) or not is_strict_int(upper):
            raise ValueError("Random integer bounds must be integers")
        return self._random.randint(lower, upper)

    def sample(self, items: Sequence[T], count: int) -> list[T]:
        if not is_strict_int(count):
            raise ValueError("Sample count must be an integer")
        if count > len(items):
            raise ValueError("Sample size exceeds available items")
        return self._random.sample(list(items), count)

    def spawn(self, salt: int) -> SeededRNG:
        if not is_strict_int(salt):
            raise ValueError("Spawn salt must be an integer")
        combined = self._random.randint(0, 2**63 - 1) ^ salt
        return SeededRNG(combined)

    def advance(self, steps: int) -> None:
        for _ in range(max(0, steps)):
            self._random.random()

    def iter_shuffle(self, items: Sequence[T], rounds: int) -> Iterable[list[T]]:
        for _ in range(rounds):
            yield self.shuffle(items)


def validate_seed(seed: int | None) -> None:
    if seed is not None and not is_strict_int(seed):
        raise ValueError("Seed must be an integer or None")


__all__ = ["SeededRNG", "validate_seed"]
