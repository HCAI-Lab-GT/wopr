"""Edition variant metadata for deterministic Nuclear War v1."""

from __future__ import annotations

from dataclasses import dataclass

from .replay_field_validation import validate_field_set

ACTIVE_VARIANT_ID = "base_later_two_d10"


@dataclass(frozen=True)
class RulesVariant:
    variant_id: str
    hand_draw_target: int
    population_deck_size: int
    randomizer: str
    initial_face_down_cards: int
    anti_missile_turn_jump: bool
    expansion_sets: tuple[str, ...]
    special_powers_enabled: bool
    trading_enabled: bool
    press_enabled: bool
    simultaneous_orders: bool

    def to_payload(self) -> dict[str, object]:
        return {
            "variant_id": self.variant_id,
            "hand_draw_target": self.hand_draw_target,
            "population_deck_size": self.population_deck_size,
            "randomizer": self.randomizer,
            "initial_face_down_cards": self.initial_face_down_cards,
            "anti_missile_turn_jump": self.anti_missile_turn_jump,
            "expansion_sets": list(self.expansion_sets),
            "special_powers_enabled": self.special_powers_enabled,
            "trading_enabled": self.trading_enabled,
            "press_enabled": self.press_enabled,
            "simultaneous_orders": self.simultaneous_orders,
        }


def validate_active_variant_payload(payload: object, context: str) -> None:
    if not isinstance(payload, dict):
        raise ValueError(f"{context} active_variant must be an object")
    expected = ACTIVE_VARIANT.to_payload()
    validate_field_set(payload, expected, f"{context} active_variant")
    for field, expected_value in expected.items():
        if field not in payload:
            raise ValueError(
                f"{context} active_variant missing required field: {field}"
            )
        actual_value = payload[field]
        if (
            type(actual_value) is not type(expected_value)
            or actual_value != expected_value
        ):
            raise ValueError(
                f"{context} active_variant has invalid {field}: {actual_value}"
            )


ACTIVE_VARIANT = RulesVariant(
    variant_id=ACTIVE_VARIANT_ID,
    hand_draw_target=10,
    population_deck_size=40,
    randomizer="base_two_d10_fallout_chart",
    initial_face_down_cards=2,
    anti_missile_turn_jump=True,
    expansion_sets=(),
    special_powers_enabled=False,
    trading_enabled=False,
    press_enabled=False,
    simultaneous_orders=False,
)

__all__ = [
    "ACTIVE_VARIANT",
    "ACTIVE_VARIANT_ID",
    "RulesVariant",
    "validate_active_variant_payload",
]
