"""Game-state construction helpers."""

from __future__ import annotations

from .cards_registry import build_deck_from_registry, load_card_registry
from .engine.draw import draw_phase, set_face_down_cards
from .modes import ruleset_for_mode
from .players import player_ids
from .population import build_population_deck, population_cards_per_player
from .press import reject_press_mode
from .rng import SeededRNG
from .rules import RULES_PATH
from .state import FACE_DOWN_SLOTS, GameState, create_players
from .variant_catalog import resolve_requested_variant
from .variants import ACTIVE_VARIANT_ID, RulesVariant


def create_game_state(
    mode: str,
    player_count: int = 2,
    seed: int | None = None,
    press: bool = False,
    variant_id: str = ACTIVE_VARIANT_ID,
    defer_opening_commitment: bool = False,
) -> GameState:
    reject_press_mode(press)
    variant = resolve_requested_variant(variant_id, "Setup")
    ruleset = ruleset_for_mode(mode)
    ids = player_ids(player_count)
    rng = SeededRNG(seed)
    registry = load_card_registry(RULES_PATH)
    deck = build_deck_from_registry(registry)
    state = GameState(
        ruleset=ruleset,
        players=create_players(ids, starting_population=30),
        draw_pile=rng.shuffle(deck),
        rng=rng.spawn(1),
        press_enabled=press,
        variant_id=variant.variant_id,
    )
    state.register_cards(deck)
    deal_population(state, rng.spawn(2))
    deal_opening_setup(
        state, variant, defer_opening_commitment=defer_opening_commitment
    )
    return state


def deal_population(state: GameState, rng: SeededRNG) -> None:
    """Deal each player their population cards from a seeded 40-card deck.

    Each player receives ``population_cards_per_player`` cards by player count; the
    remaining cards form the population bank. The full 240M deck is conserved across
    every player plus the bank. (Per-transaction make-change against the bank is a
    documented V1 deferral; the bank is the initial leftover pool.)
    """
    deck = rng.shuffle(build_population_deck())
    per_player = population_cards_per_player(len(state.players))
    index = 0
    for player in state.players.values():
        player.population = deck[index : index + per_player]
        index += per_player
    state.population_bank = deck[index:]


def deal_opening_setup(
    state: GameState,
    variant: RulesVariant | None = None,
    defer_opening_commitment: bool = False,
) -> None:
    """Deal each player a full opening hand, then commit the face-down launch track.

    Faithful to the rules' opening: a player is dealt up to the hand draw target with
    Secrets routed out of the hand (parked, never sitting face-up or face-down), then
    commits ``initial_face_down_cards`` cards from that secret-free hand onto the
    launch track. For the active ``base_later_two_d10`` variant this leaves 8 cards in
    hand plus 2 face-down, so the post-setup draw count equals the hand draw target.

    Parked initial Secrets are resolved on each player's first turn (table mode in the
    turn driver; postal mode through its player-targeted secret phase) so the
    resolution events — including any elimination — are captured in the replay log.
    """
    resolved = variant or resolve_requested_variant(state.variant_id, "Setup")
    deal_opening_hands(state)
    if defer_opening_commitment:
        # The table decision loop surfaces the commitment as SETUP_PLACE decisions
        # (the rules make the two opening face-down cards a strategic choice); the
        # loop's options[0] ordering reproduces the auto-commit hand[:2] behavior.
        return
    commit_initial_face_down_cards(state, resolved)


def deal_opening_hands(state: GameState) -> None:
    """Deal each player up to the hand draw target, parking Secrets out of hand."""
    for player_id in state.players:
        draw_phase(state, player_id)


def commit_initial_face_down_cards(
    state: GameState,
    variant: RulesVariant | None = None,
) -> None:
    """Move the opening face-down cards from each player's hand onto the track."""
    resolved = variant or resolve_requested_variant(state.variant_id, "Setup")
    count = min(resolved.initial_face_down_cards, FACE_DOWN_SLOTS)
    for player in state.players.values():
        player.face_down_queue.clear()
        player.face_down_queue.extend([None] * FACE_DOWN_SLOTS)
        set_face_down_cards(player, list(player.hand[:count]))


# Backwards-compatible alias: the public setup entry point used to deal only the
# face-down cards. It now runs the full faithful opening setup.
deal_initial_face_down_cards = deal_opening_setup


__all__ = [
    "create_game_state",
    "deal_population",
    "deal_opening_setup",
    "deal_opening_hands",
    "commit_initial_face_down_cards",
    "deal_initial_face_down_cards",
]
