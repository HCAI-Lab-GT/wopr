"""Rules validation helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .card_effect_evidence import (
    CARD_EFFECT_EVIDENCE_PATH,
    validate_card_effect_evidence_manifest,
)
from .cards_registry import build_deck_from_registry, load_card_registry
from .engine.postal import PHASE_HANDLERS
from .engine.postal.secret_effects import SUPPORTED_EFFECT_KEYS
from .expansion_composition_evidence import (
    EXPANSION_COMPOSITION_EVIDENCE_PATH,
    validate_expansion_composition_evidence_manifest,
)
from .expansions import catalog_effects, catalog_payload
from .registry_file_validation import registry_file_issues
from .rules_effect_validation import postal_special_effects, unsupported_effect_keys
from .rules_expansion_validation import validate_expansion_mechanics
from .rules_trace import (
    rules_trace_payload,
    rules_trace_source_gaps,
    rules_trace_step_gaps,
    rules_trace_step_payload,
    rules_trace_step_source_gaps,
)
from .rules_trace_replay import (
    rules_trace_full_game_gaps,
    rules_trace_full_game_summary,
)
from .source_blockers import source_blocker_payload
from .source_evidence_coverage import (
    card_effect_evidence_coverage_for_registry,
    expansion_composition_evidence_coverage,
)
from .source_evidence_promotion import (
    card_effect_promotion_errors,
    expansion_composition_promotion_errors,
)
from .source_index_validation import SOURCE_INDEX_PATH, validate_source_index
from .source_validation import (
    invalid_confidence_fields,
    invalid_count_fields,
    invalid_source_fields,
    metadata_records_in_deck,
    missing_confidence_fields,
    missing_source_fields,
    restricted_text_fields,
    unresolved_source_labels,
)
from .variant_catalog import variant_catalog_gaps, variant_catalog_payload
from .variants import ACTIVE_VARIANT

RULES_PATH = (
    Path(__file__).resolve().parents[2] / "rules" / "nuclear_war_base_cards.jsonl"
)
RESTRICTED_TEXT_FIELDS = {
    "exact_front_text",
    "exact_text",
    "image_filename_private_only",
    "official_text",
    "unofficial_text",
}
REQUIRED_POSTAL_PHASES = set(
    "cruise_move declare_targets enqueue espionage final_strike flip_queue "
    "intercept launch nuking peace propaganda sabotage secrets specials "
    "submarines".split()
)


def validate_rules(
    path: Path = RULES_PATH,
    source_index_path: Path = SOURCE_INDEX_PATH,
    card_effect_evidence_path: Path = CARD_EFFECT_EVIDENCE_PATH,
    expansion_composition_evidence_path: Path = EXPANSION_COMPOSITION_EVIDENCE_PATH,
) -> dict[str, Any]:
    file_issues = registry_file_issues(path)
    malformed_lines = file_issues["malformed_registry_lines"]
    invalid_ids = file_issues["invalid_card_ids"]
    invalid_types = file_issues["invalid_card_types"]
    duplicate_ids = file_issues["duplicate_card_ids"]
    registry = (
        {}
        if malformed_lines or invalid_ids or invalid_types
        else load_card_registry(path)
    )
    invalid_names = [
        {"card_id": record.identifier, "name": record.name}
        for record in registry.values()
        if not isinstance(record.name, str) or not record.name.strip()
    ]
    invalid_counts = invalid_count_fields(registry)
    deck = [] if invalid_counts or invalid_names else build_deck_from_registry(registry)
    phase_names = {name for name, _handler in PHASE_HANDLERS}
    missing = sorted(REQUIRED_POSTAL_PHASES - phase_names)
    unsupported_effects = unsupported_effect_keys(registry)
    restricted_fields = restricted_text_fields(registry, RESTRICTED_TEXT_FIELDS)
    source_index = validate_source_index(source_index_path)
    card_effect_evidence = validate_card_effect_evidence_manifest(
        card_effect_evidence_path,
        known_card_ids=set(registry),
    )
    card_effect_evidence_errors = (
        card_effect_evidence.errors if card_effect_evidence.present else []
    )
    card_effect_coverage = card_effect_evidence_coverage_for_registry(
        card_effect_evidence_path,
        registry,
    )
    card_effect_promotion = card_effect_promotion_errors(card_effect_evidence_path)
    expansion_composition_evidence = validate_expansion_composition_evidence_manifest(
        expansion_composition_evidence_path
    )
    expansion_composition_evidence_errors = (
        expansion_composition_evidence.errors
        if expansion_composition_evidence.present
        else []
    )
    expansion_composition_coverage = expansion_composition_evidence_coverage(
        expansion_composition_evidence_path
    )
    expansion_composition_promotion = expansion_composition_promotion_errors(
        expansion_composition_evidence_path
    )
    source_ids = source_index.ids
    trace_source_gaps = rules_trace_source_gaps(source_ids)
    trace_step_gaps = rules_trace_step_gaps()
    trace_step_source_gaps = rules_trace_step_source_gaps(source_ids)
    full_game_trace_gaps = rules_trace_full_game_gaps()
    missing_sources = missing_source_fields(registry)
    invalid_sources = invalid_source_fields(registry)
    missing_confidence = missing_confidence_fields(registry)
    invalid_confidence = invalid_confidence_fields(registry)
    source_labels = unresolved_source_labels(registry, source_ids)
    variant_gaps = variant_catalog_gaps(source_ids)
    postal_effects = postal_special_effects(registry)
    expansion_validation = validate_expansion_mechanics(registry)
    metadata_deck_records = metadata_records_in_deck(registry)
    missing_postal_special_effects = sorted(catalog_effects() - set(postal_effects))
    failures = [
        malformed_lines,
        invalid_ids,
        invalid_types,
        invalid_names,
        duplicate_ids,
        missing,
        unsupported_effects,
        restricted_fields,
        missing_sources,
        invalid_sources,
        missing_confidence,
        invalid_confidence,
        invalid_counts,
        source_labels,
        source_index.errors,
        card_effect_evidence_errors,
        card_effect_promotion,
        expansion_composition_evidence_errors,
        expansion_composition_promotion,
        trace_source_gaps,
        trace_step_gaps,
        trace_step_source_gaps,
        full_game_trace_gaps,
        variant_gaps,
        metadata_deck_records,
        missing_postal_special_effects,
        *expansion_validation.values(),
    ]
    return {
        "ok": bool(registry) and bool(deck) and bool(source_ids) and not any(failures),
        "card_records": len(registry),
        "deck_size": len(deck),
        "malformed_registry_lines": malformed_lines,
        "invalid_card_ids": invalid_ids,
        "invalid_card_names": invalid_names,
        "invalid_card_types": invalid_types,
        "duplicate_card_ids": duplicate_ids,
        "postal_phases": sorted(phase_names),
        "missing_postal_phases": missing,
        "supported_effect_keys": sorted(SUPPORTED_EFFECT_KEYS),
        "unsupported_effect_keys": unsupported_effects,
        "restricted_text_fields": restricted_fields,
        "source_index_id_count": len(source_ids),
        "source_blockers": source_blocker_payload(),
        "rules_trace": rules_trace_payload(),
        "rules_trace_source_gaps": trace_source_gaps,
        "rules_trace_steps": rules_trace_step_payload(),
        "rules_trace_step_gaps": trace_step_gaps,
        "rules_trace_step_source_gaps": trace_step_source_gaps,
        "rules_trace_full_game": rules_trace_full_game_summary(),
        "rules_trace_full_game_gaps": full_game_trace_gaps,
        "source_index_errors": source_index.errors,
        "card_effect_evidence_manifest": card_effect_evidence.to_payload(),
        "card_effect_evidence_manifest_errors": card_effect_evidence_errors,
        "card_effect_evidence_coverage": card_effect_coverage.to_payload(),
        "card_effect_evidence_promotion_errors": card_effect_promotion,
        "expansion_composition_evidence_manifest": (
            expansion_composition_evidence.to_payload()
        ),
        "expansion_composition_evidence_manifest_errors": (
            expansion_composition_evidence_errors
        ),
        "expansion_composition_evidence_coverage": (
            expansion_composition_coverage.to_payload()
        ),
        "expansion_composition_evidence_promotion_errors": (
            expansion_composition_promotion
        ),
        "missing_source_fields": missing_sources,
        "invalid_source_fields": invalid_sources,
        "missing_confidence_fields": missing_confidence,
        "invalid_confidence_fields": invalid_confidence,
        "invalid_count_fields": invalid_counts,
        "unresolved_source_labels": source_labels,
        "metadata_records_in_deck": metadata_deck_records,
        "postal_special_effects": postal_effects,
        "missing_postal_special_effects": missing_postal_special_effects,
        "expansion_mechanics": catalog_payload(),
        **expansion_validation,
        "active_variant": ACTIVE_VARIANT.to_payload(),
        "variant_catalog": variant_catalog_payload(),
        "variant_catalog_gaps": variant_gaps,
        "press_enabled": False,
    }
