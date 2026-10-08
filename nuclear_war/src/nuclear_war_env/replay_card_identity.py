"""Replay card identity validation helpers."""

from __future__ import annotations


def validate_card_id(value: str, message: str) -> None:
    if not value:
        raise ValueError(message)


def validate_card_id_list(values: list[str], message: str) -> None:
    if not all(values):
        raise ValueError(message)


__all__ = ["validate_card_id", "validate_card_id_list"]
