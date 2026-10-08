"""Rules trace step catalog rows."""

from __future__ import annotations

RuleStepRow = tuple[str, str, str, tuple[str, ...]]

BASE_SOURCE = ("MIR-001",)
SLIDE_SOURCE = ("MIR-001", "MIR-002")


def _step(
    step_id: str,
    rule_area: str,
    summary: str,
    source_ids: tuple[str, ...] = BASE_SOURCE,
) -> RuleStepRow:
    return (step_id, rule_area, summary, source_ids)


RULE_STEP_ROWS: tuple[RuleStepRow, ...] = (
    _step(
        "slide_launch_track",
        "turn",
        "Move queued face-down cards toward face-up resolution.",
        SLIDE_SOURCE,
    ),
    _step("draw_to_hand_target", "turn", "Draw until the active hand target is met."),
    _step("place_face_down_card", "turn", "Place one card into the face-down queue."),
    _step(
        "commit_opening_strategy",
        "setup",
        "Commit the opening face-down cards as a strategic choice.",
    ),
    _step(
        "peace_strategy_replacement",
        "peace",
        "Replace one or two face-down cards from hand when peace is restored.",
    ),
    _step(
        "modify_deterrents",
        "turn",
        "Update deterrent cards during the turn window.",
    ),
    _step(
        "resolve_face_up_card",
        "turn",
        "Resolve the card moved into the face-up slot.",
    ),
    _step("load_delivery_system", "attack", "Keep an eligible delivery system ready."),
    _step(
        "discard_attack_cards",
        "attack",
        "Discard attack cards after use or failure.",
    ),
    _step(
        "declare_attack_target",
        "attack",
        "Choose the target of a launched warhead.",
    ),
    _step(
        "defender_intercept_response",
        "attack",
        "Let the defender respond to an attack.",
    ),
    _step("resolve_attack", "attack", "Resolve a launched warhead against its target."),
    _step("apply_fallout_randomizer", "attack", "Apply the fallout randomizer result."),
    _step(
        "apply_population_loss",
        "population",
        "Apply population loss from an attack.",
    ),
    _step(
        "apply_elimination",
        "population",
        "Handle a player with no population left.",
    ),
    _step(
        "restore_peace_after_elimination",
        "population",
        "Restore peace after elimination and pending final strikes resolve.",
    ),
    _step(
        "resolve_secret_or_top_secret",
        "secret",
        "Resolve a drawn or queued secret effect.",
    ),
    _step("secret_effect", "secret", "Apply a secret effect to population or turns."),
    _step(
        "resolve_peace_propaganda",
        "propaganda",
        "Apply propaganda while peace is active.",
    ),
    _step(
        "final_retaliation_targeting",
        "final_strike",
        "Choose targets for immediate final retaliation.",
    ),
    _step(
        "final_retaliation",
        "final_strike",
        "Resolve final retaliation and any chained eliminations.",
    ),
)


__all__ = ["RULE_STEP_ROWS", "RuleStepRow"]
