"""Shared card category predicates."""

from __future__ import annotations

from .cards import CardCategory


def is_secret_like(category: CardCategory) -> bool:
    return category in {CardCategory.SECRET, CardCategory.TOP_SECRET}


__all__ = ["is_secret_like"]
