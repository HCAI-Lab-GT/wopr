"""Attack-resolution correctness: backfire, intercept selection, global loss."""

from __future__ import annotations

from collections import Counter

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.launch import execute_launches
from nuclear_war_env.engine.launch_helpers import attempt_intercept
from nuclear_war_env.engine.launch_resolution import (
    resolve_unblocked_launch,
    trigger_global_loss,
)
from nuclear_war_env.fallout import resolve_spinner
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state() -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(
            ["player_0", "player_1", "player_2"], starting_population=30
        ),
        draw_pile=[],
    )
    state.register_cards(
        [Card("missile", CardCategory.DELIVERY, "Missile", metadata={"capacity": 1})]
    )
    return state


def _order() -> dict[str, object]:
    return {"delivery": "missile", "warheads": ["w"], "target": "player_1"}


def test_missile_booster_explodes_backfires_warhead_yield_on_attacker() -> None:
    state = _state()
    state.population_bank = [10, 5]
    outcome = resolve_spinner(0)  # 00-04: booster explodes / attacker backfire

    events = resolve_unblocked_launch(
        state,
        "player_0",
        "player_1",
        "missile",
        _order(),
        total_yield=10,
        outcome=outcome,
    )

    # The booster explodes on the attacker for the warhead's yield; target is unhit.
    assert sum(state.players["player_0"].population) == 20  # 30 - 10 backfire
    assert sum(state.players["player_1"].population) == 30  # untouched
    assert any(event.event_type == "launch_backfire" for event in events)


def test_booster_self_elimination_grants_final_retaliation() -> None:
    # Rules: final retaliation follows any death by warhead; only a propaganda
    # defeat forfeits it. A booster explosion is a warhead death.
    state = _state()
    state.register_cards(
        [
            Card(
                "ret_missile",
                CardCategory.DELIVERY,
                "Missile",
                metadata={"capacity": 1},
            ),
            Card("ret_warhead", CardCategory.WARHEAD, "Warhead", value=10),
        ]
    )
    state.population_bank = [10, 5, 5, 2, 2, 1]
    attacker = state.players["player_0"]
    attacker.population = [5]
    attacker.hand = ["ret_missile", "ret_warhead"]
    outcome = resolve_spinner(0)  # booster explodes; yield 10 kills the attacker

    events = resolve_unblocked_launch(
        state,
        "player_0",
        "player_1",
        "missile",
        _order(),
        total_yield=10,
        outcome=outcome,
    )

    assert not attacker.alive
    event_types = [event.event_type for event in events]
    assert "player_eliminated" in event_types
    assert "final_strike_executed" in event_types
    # A spinner_result after the elimination proves the retaliation launch
    # actually resolved rather than being scheduled and dropped.
    assert event_types.index("final_strike_executed") > event_types.index(
        "player_eliminated"
    )
    assert "spinner_result" in event_types


def _force_booster_explodes(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from nuclear_war_env.fallout import resolve_spinner

    monkeypatch.setattr(
        "nuclear_war_env.engine.launch.spin_spinner",
        lambda rng: (0, resolve_spinner(0)),  # 00-04: booster explodes
    )


def _self_kill_state():  # type: ignore[no-untyped-def]
    state = _state()
    state.register_cards([Card("warhead", CardCategory.WARHEAD, "Warhead", value=10)])
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    attacker = state.players["player_0"]
    attacker.population = [5]  # dies to its own 10 Mt booster backfire
    attacker.pending_orders["launches"] = {
        "missile": {
            "delivery": "missile",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "player_1",
        }
    }
    return state


def test_booster_self_kill_does_not_refire_the_exploded_launch(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # Regression: the missile that exploded on the launch pad
    # must not be copied into the retaliation pool and fired/discarded a second
    # time. With no other arsenal there is no retaliation at all.
    from nuclear_war_env.engine.launch import execute_launches

    state = _self_kill_state()
    _force_booster_explodes(monkeypatch)

    events = execute_launches(state)

    assert not state.players["player_0"].alive
    event_types = [event.event_type for event in events]
    assert event_types.count("spinner_result") == 1  # only the backfire roll
    assert "final_strike_executed" not in event_types
    assert sum(state.players["player_1"].population) == 30  # target untouched
    discarded = [card.identifier for card in state.discard_pile]
    assert discarded.count("missile") == 1
    assert discarded.count("warhead") == 1


def test_booster_self_kill_still_retaliates_from_other_arsenal(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    # The privilege still applies: retaliation fires from the hand arsenal, just
    # not from the exploded launch.
    from nuclear_war_env.engine.launch import execute_launches

    state = _self_kill_state()
    state.register_cards(
        [
            Card(
                "ret_missile",
                CardCategory.DELIVERY,
                "Missile",
                metadata={"capacity": 1},
            ),
            Card("ret_warhead", CardCategory.WARHEAD, "Warhead", value=10),
        ]
    )
    state.players["player_0"].hand = ["ret_missile", "ret_warhead"]
    _force_booster_explodes(monkeypatch)

    events = execute_launches(state)

    assert not state.players["player_0"].alive
    event_types = [event.event_type for event in events]
    assert "final_strike_executed" in event_types
    # Two spinner rolls: the backfire, then the retaliation launch.
    assert event_types.count("spinner_result") == 2
    discarded = [card.identifier for card in state.discard_pile]
    assert discarded.count("warhead") == 1  # the exploded warhead, discarded once


def test_launch_backfire_returns_population_cards_to_bank() -> None:
    state = _state()
    state.players["player_0"].population = [5]
    state.population_bank = [2, 1, 1, 1]
    outcome = resolve_spinner(0)

    events = resolve_unblocked_launch(
        state,
        "player_0",
        "player_1",
        "missile",
        _order(),
        total_yield=3,
        outcome=outcome,
    )

    assert state.players["player_0"].population == [2]
    assert Counter(state.population_bank) == Counter([5, 1, 1, 1])
    assert any(
        event.event_type == "launch_backfire" and event.payload.get("loss") == 3
        for event in events
    )


def test_launch_damage_returns_population_cards_to_bank() -> None:
    state = _state()
    state.players["player_1"].population = [5]
    state.population_bank = [2, 1, 1, 1]
    outcome = resolve_spinner(40)

    events = resolve_unblocked_launch(
        state,
        "player_0",
        "player_1",
        "missile",
        _order(),
        total_yield=3,
        outcome=outcome,
    )

    assert state.players["player_1"].population == [2]
    assert Counter(state.population_bank) == Counter([5, 1, 1, 1])
    assert any(
        event.event_type == "warhead_detonated" and event.payload.get("loss") == 3
        for event in events
    )


def test_bomber_out_of_fuel_does_not_backfire_on_attacker() -> None:
    state = _state()
    state.register_cards(
        [Card("b70", CardCategory.DELIVERY, "B-70 Bomber", metadata={"capacity": 2})]
    )
    order = {"delivery": "b70", "warheads": ["w"], "target": "player_1"}
    outcome = resolve_spinner(0)  # 00-04: a missile booster explodes...

    events = resolve_unblocked_launch(
        state, "player_0", "player_1", "b70", order, total_yield=10, outcome=outcome
    )

    # ...but a bomber merely runs out of fuel: no backfire, no one is hit.
    assert sum(state.players["player_0"].population) == 30
    assert sum(state.players["player_1"].population) == 30
    assert not any(event.event_type == "launch_backfire" for event in events)


def test_target_intercepts_reactively_from_hand() -> None:
    state = _state()
    state.register_cards(
        [
            Card(
                "polaris",
                CardCategory.DELIVERY,
                "Polaris Missile",
                metadata={"capacity": 1, "intercept_by": ("P",)},
            ),
            Card("w10", CardCategory.WARHEAD, "Warhead 10 Mt", value=10),
            Card(
                "amP",
                CardCategory.ANTIMISSILE,
                "Anti-Missile (P)",
                metadata={"label": "P"},
            ),
        ]
    )
    state.players["player_0"].pending_orders["launches"] = {
        "polaris": {
            "delivery": "polaris",
            "capacity": 1,
            "warheads": ["w10"],
            "target": "player_1",
        }
    }
    # The defender holds a matching anti-missile in HAND (not pre-placed on a track).
    state.players["player_1"].hand = ["amP"]

    events = execute_launches(state)

    assert any(event.event_type == "intercept_success" for event in events)
    assert "amP" not in state.players["player_1"].hand  # played from hand
    assert not any(event.event_type == "warhead_detonated" for event in events)
    assert sum(state.players["player_1"].population) == 30  # attack blocked


def test_attempt_intercept_skips_ineligible_hand_card() -> None:
    state = _state()
    # An ineligible anti-missile (only stops yield <= 5) and an eligible one ("any")
    # in hand; a 10-yield attack must use the eligible one.
    state.register_cards(
        [
            Card("weak", CardCategory.ANTIMISSILE, "Weak", metadata={"intercept": 5}),
            Card("any", CardCategory.ANTIMISSILE, "Any", metadata={"intercept": "any"}),
        ]
    )
    target = state.players["player_1"]
    target.hand = ["weak", "any"]
    delivery = state.card_by_id("missile")

    chosen = attempt_intercept(state, target, total_yield=10, delivery=delivery)

    assert chosen == "any"
    assert target.hand == ["weak"]  # eligible one consumed only


def test_global_loss_eliminates_every_player_with_valid_events() -> None:
    state = _state()  # 3 players alive

    events = trigger_global_loss(state, "player_0", "player_1")

    assert all(not player.alive for player in state.players.values())
    assert all(sum(player.population) == 0 for player in state.players.values())
    assert any(event.event_type == "global_loss" for event in events)
    eliminated = {
        event.player_id: event.payload["by"]
        for event in events
        if event.event_type == "player_eliminated"
    }
    # Every player has an elimination event whose "by" is not themselves.
    assert set(eliminated) == {"player_0", "player_1", "player_2"}
    assert all(by != player_id for player_id, by in eliminated.items())
