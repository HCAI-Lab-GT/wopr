"""Game setup tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.card_kinds import is_secret_like
from nuclear_war_env.cards_registry import load_card_registry
from nuclear_war_env.hand_count import draw_count
from nuclear_war_env.population import population_cards_per_player
from nuclear_war_env.rules import RULES_PATH
from nuclear_war_env.setup_game import create_game_state
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_setup_deals_population_from_the_40_card_deck_with_a_conserved_bank() -> None:
    state = create_game_state("table", player_count=3, seed=0)
    per_player = population_cards_per_player(3)
    for player in state.players.values():
        assert len(player.population) == per_player
    dealt = sum(len(player.population) for player in state.players.values())
    assert len(state.population_bank) == 40 - dealt
    total = sum(sum(player.population) for player in state.players.values()) + sum(
        state.population_bank
    )
    assert total == 240  # the full deck is conserved across players + bank


def test_setup_population_deal_varies_by_seed() -> None:
    first = create_game_state("table", player_count=3, seed=0)
    second = create_game_state("table", player_count=3, seed=1)
    first_totals = sorted(sum(p.population) for p in first.players.values())
    second_totals = sorted(sum(p.population) for p in second.players.values())
    assert first_totals != second_totals


def test_create_game_state_records_active_variant() -> None:
    state = create_game_state("table", player_count=2, seed=0)
    assert state.variant_id == "base_later_two_d10"


def test_create_game_state_deals_opening_hand_to_draw_target() -> None:
    state = create_game_state("table", player_count=3, seed=0)
    in_hand = ACTIVE_VARIANT.hand_draw_target - ACTIVE_VARIANT.initial_face_down_cards
    for player in state.players.values():
        assert len(player.hand) == in_hand
        assert draw_count(player) == ACTIVE_VARIANT.hand_draw_target


def test_table_setup_keeps_secrets_out_of_hand_and_face_down() -> None:
    # Run several seeds so at least one deals an opening secret.
    for seed in range(8):
        state = create_game_state("table", player_count=3, seed=seed)
        for player in state.players.values():
            in_play = list(player.hand) + [
                card_id for card_id in player.face_down_queue if card_id is not None
            ]
            # No Secret/Top Secret ever sits in hand or on the face-down track;
            # drawn secrets are parked for resolution on the player's first turn.
            assert all(
                not is_secret_like(state.card_by_id(card_id).category)
                for card_id in in_play
            )
            assert all(
                is_secret_like(state.card_by_id(card_id).category)
                for card_id in player.secrets
            )


def test_create_game_state_deals_initial_face_down_cards() -> None:
    state = create_game_state("table", player_count=3, seed=0)
    queued = {
        player_id: list(player.face_down_queue)
        for player_id, player in state.players.items()
    }
    queued_cards = [
        card_id for cards in queued.values() for card_id in cards if card_id is not None
    ]
    registry = load_card_registry(RULES_PATH)
    expected_deck_size = sum(record.count for record in registry.values())

    assert all(len(cards) == 2 for cards in queued.values())
    assert all(
        all(card_id is not None for card_id in cards) for cards in queued.values()
    )
    assert len(queued_cards) == 6
    # Every card is conserved across the draw pile, discard, hands, and the
    # face-down launch tracks once opening hands are dealt.
    in_hands = sum(len(player.hand) for player in state.players.values())
    accounted = (
        len(state.draw_pile) + len(state.discard_pile) + in_hands + len(queued_cards)
    )
    assert accounted == expected_deck_size


def test_create_game_state_registers_every_physical_card_copy() -> None:
    state = create_game_state("table", player_count=3, seed=0)
    registry = load_card_registry(RULES_PATH)
    expected_deck_size = sum(record.count for record in registry.values())
    assert len(state.card_lookup) == expected_deck_size


def test_create_game_state_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="Unknown mode: space"):
        create_game_state("space", player_count=2, seed=0)


def test_create_game_state_rejects_unknown_mode_before_loading_rules(
    monkeypatch,
) -> None:
    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid mode")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    with pytest.raises(ValueError, match="Unknown mode: space"):
        create_game_state("space", player_count=2, seed=0)


def test_create_game_state_rejects_press_mode() -> None:
    with pytest.raises(ValueError, match="Postal press is deferred"):
        create_game_state("postal", player_count=2, seed=0, press=True)


def test_create_game_state_rejects_one_player_game() -> None:
    with pytest.raises(ValueError, match="At least two players are required"):
        create_game_state("table", player_count=1, seed=0)


def test_create_game_state_rejects_one_player_game_before_loading_rules(
    monkeypatch,
) -> None:
    def fail_load_rules(_path):
        raise AssertionError("rules should not load for invalid player count")

    monkeypatch.setattr(
        "nuclear_war_env.setup_game.load_card_registry", fail_load_rules
    )
    with pytest.raises(ValueError, match="At least two players are required"):
        create_game_state("table", player_count=1, seed=0)
