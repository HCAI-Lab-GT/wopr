"""Postal space equipment setup legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .actions_postal_space_setup_queue import apply_space_setup_action
from .cards import CardCategory
from .engine.postal.space_platform import MAX_PLATFORM_WARHEADS
from .integer_validation import positive_int_or_zero
from .state import GameState

SPACE_SETUP_TYPES = {
    ActionType.POSTAL_SPACE_PLATFORM_LAUNCH,
    ActionType.POSTAL_SPACE_SHUTTLE_RELOAD,
    ActionType.POSTAL_SPACE_SHUTTLE_ATTACK,
    ActionType.POSTAL_KILLER_SATELLITE_LAUNCH,
}


def space_setup_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions = _platform_launch_actions(state, player_id)
    actions.extend(_shuttle_reload_actions(state, player_id))
    actions.extend(_shuttle_attack_actions(state, player_id))
    actions.extend(_satellite_launch_actions(state, player_id))
    return actions


def _platform_launch_actions(state: GameState, player_id: str) -> list[LegalAction]:
    warheads = _hand_warheads(state, player_id)
    if not warheads:
        return []
    return [
        build_action(
            player_id,
            ActionType.POSTAL_SPACE_PLATFORM_LAUNCH,
            "Launch space platform",
            {"card": card_id, "warheads": [item[0] for item in warheads]},
        )
        for card_id in _hand_specials(state, player_id, "space_platform")
    ]


def _shuttle_reload_actions(state: GameState, player_id: str) -> list[LegalAction]:
    platforms = state.players[player_id].pending_orders.get("space_platforms", {})
    warheads = _hand_warheads(state, player_id)
    if not isinstance(platforms, dict) or not warheads:
        return []
    actions: list[LegalAction] = []
    for card_id in _hand_specials(state, player_id, "space_shuttle"):
        for platform_id in platforms:
            actions.append(
                build_action(
                    player_id,
                    ActionType.POSTAL_SPACE_SHUTTLE_RELOAD,
                    f"Reload space platform {platform_id}",
                    {
                        "card": card_id,
                        "platform": str(platform_id),
                        "warheads": [item[0] for item in warheads],
                    },
                )
            )
    return actions


def _shuttle_attack_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions: list[LegalAction] = []
    for card_id in _hand_specials(state, player_id, "space_shuttle"):
        for warhead_id, _payload in _hand_warheads(state, player_id):
            actions.extend(
                _targeted_shuttle_actions(state, player_id, card_id, warhead_id)
            )
    return actions


def _targeted_shuttle_actions(
    state: GameState, player_id: str, card_id: str, warhead_id: str
) -> list[LegalAction]:
    actions: list[LegalAction] = []
    for target_id, target in state.players.items():
        if target_id == player_id or not target.alive:
            continue
        actions.append(
            build_action(
                player_id,
                ActionType.POSTAL_SPACE_SHUTTLE_ATTACK,
                f"Attack {target_id} with space shuttle",
                {"card": card_id, "target": target_id, "warhead": warhead_id},
            )
        )
    return actions


def _satellite_launch_actions(state: GameState, player_id: str) -> list[LegalAction]:
    return [
        build_action(
            player_id,
            ActionType.POSTAL_KILLER_SATELLITE_LAUNCH,
            "Launch killer satellite",
            {"card": card_id},
        )
        for card_id in _hand_specials(state, player_id, "killer_satellite")
    ]


def _hand_specials(state: GameState, player_id: str, postal_effect: str) -> list[str]:
    return [
        card_id
        for card_id in state.players[player_id].hand
        if state.card_by_id(card_id).category is CardCategory.SPECIAL
        and state.card_by_id(card_id).metadata.get("postal_effect") == postal_effect
    ]


def _hand_warheads(state: GameState, player_id: str) -> list[tuple[str, int]]:
    result: list[tuple[str, int]] = []
    for card_id in state.players[player_id].hand:
        if state.card_by_id(card_id).category is not CardCategory.WARHEAD:
            continue
        payload = _warhead_payload(state, card_id)
        if payload > 0:
            result.append((card_id, payload))
    return result[:MAX_PLATFORM_WARHEADS]


def _warhead_payload(state: GameState, card_id: str) -> int:
    card = state.card_by_id(card_id)
    value = card.value or card.metadata.get("yield_megatons", 0)
    return positive_int_or_zero(value)


__all__ = ["SPACE_SETUP_TYPES", "apply_space_setup_action", "space_setup_actions"]
