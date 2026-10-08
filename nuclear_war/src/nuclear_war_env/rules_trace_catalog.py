"""Rules trace catalog rows."""

from __future__ import annotations

TraceRow = tuple[str, str, str, str, tuple[str, ...]]

BASE_SOURCE = ("MIR-001",)
SPINNER_SOURCE = ("MIR-002",)


def _action(
    trace_id: str,
    record_type: str,
    rule_step: str,
    source_ids: tuple[str, ...] = BASE_SOURCE,
) -> TraceRow:
    return (trace_id, "action", record_type, rule_step, source_ids)


def _event(
    trace_id: str,
    record_type: str,
    rule_step: str,
    source_ids: tuple[str, ...] = BASE_SOURCE,
) -> TraceRow:
    return (trace_id, "event", record_type, rule_step, source_ids)


TRACE_ROWS: tuple[TraceRow, ...] = (
    _action("table.turn.advance", "advance", "slide_launch_track", SPINNER_SOURCE),
    _action("table.turn.draw", "draw", "draw_to_hand_target"),
    _action("table.turn.enqueue", "enqueue", "place_face_down_card"),
    _action("table.setup.place", "setup_place", "commit_opening_strategy"),
    _action(
        "table.peace.strategy_replace",
        "strategy_replace",
        "peace_strategy_replacement",
    ),
    _action("table.turn.modify_deterrent", "modify_deterrent", "modify_deterrents"),
    _action("table.attack.target", "target", "declare_attack_target"),
    _action("table.attack.intercept", "intercept", "defender_intercept_response"),
    _action("table.secret.target", "secret_target", "resolve_secret_or_top_secret"),
    _action("table.propaganda.target", "propaganda_target", "resolve_peace_propaganda"),
    _action(
        "table.final_strike.target",
        "final_strike_target",
        "final_retaliation_targeting",
    ),
    _action("table.attack.resolve", "resolve", "resolve_attack"),
    _event("table.turn.card_drawn", "card_drawn", "draw_to_hand_target"),
    _event("table.turn.cards_enqueued", "cards_enqueued", "place_face_down_card"),
    _event("table.card.resolved", "card_resolved", "resolve_face_up_card"),
    _event("table.card.delivery_ready", "delivery_ready", "resolve_face_up_card"),
    _event("table.card.warhead_loaded", "warhead_loaded", "load_delivery_system"),
    _event("table.card.warhead_discarded", "warhead_discarded", "discard_attack_cards"),
    _event("table.attack.target_declared", "target_declared", "declare_attack_target"),
    _event("table.attack.launch_declared", "launch_declared", "resolve_attack"),
    _event("table.attack.launch_backfire", "launch_backfire", "resolve_attack"),
    _event(
        "table.attack.intercept_success",
        "intercept_success",
        "defender_intercept_response",
    ),
    _event("table.attack.spinner_result", "spinner_result", "apply_fallout_randomizer"),
    _event(
        "table.attack.warhead_detonated",
        "warhead_detonated",
        "apply_population_loss",
    ),
    _event("table.attack.player_eliminated", "player_eliminated", "apply_elimination"),
    _event(
        "table.attack.peace_restored",
        "peace_restored",
        "restore_peace_after_elimination",
    ),
    _event("table.propaganda.ready", "propaganda_ready", "resolve_face_up_card"),
    _event("table.propaganda.effect", "propaganda_effect", "resolve_peace_propaganda"),
    _event("table.secret.queued", "secret_queued", "resolve_secret_or_top_secret"),
    _event(
        "table.secret.triggered",
        "secret_triggered",
        "resolve_secret_or_top_secret",
    ),
    _event(
        "table.secret.population_damaged",
        "secret_population_damaged",
        "secret_effect",
    ),
    _event(
        "table.secret.population_gained",
        "secret_population_gained",
        "secret_effect",
    ),
    _event(
        "table.secret.population_removed",
        "secret_population_removed",
        "secret_effect",
    ),
    _event(
        "table.secret.population_stolen",
        "secret_population_stolen",
        "secret_effect",
    ),
    _event("table.secret.turns_lost", "secret_turns_lost", "secret_effect"),
    _event("table.final_strike.targeted", "final_strike_targeted", "final_retaliation"),
    _event("table.final_strike.executed", "final_strike_executed", "final_retaliation"),
)


__all__ = ["TRACE_ROWS", "TraceRow"]
