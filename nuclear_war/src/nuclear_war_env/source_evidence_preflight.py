"""Draft source-evidence preflight validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .card_effect_evidence import validate_card_effect_evidence_manifest
from .cards_registry import load_card_registry
from .expansion_composition_evidence import (
    validate_expansion_composition_evidence_manifest,
)
from .rules import RULES_PATH
from .source_evidence_coverage import (
    card_effect_evidence_coverage,
    expansion_composition_evidence_coverage,
)
from .source_evidence_target_details import (
    card_effect_target_details,
    expansion_composition_target_details,
)


def validate_source_evidence_files(
    card_effect_path: Path | None = None,
    expansion_composition_path: Path | None = None,
) -> dict[str, Any]:
    if card_effect_path is None and expansion_composition_path is None:
        raise ValueError("At least one source evidence path is required")
    payload: dict[str, Any] = {"ok": True}
    if card_effect_path is not None:
        registry = load_card_registry(RULES_PATH)
        card_effect = validate_card_effect_evidence_manifest(
            card_effect_path,
            known_card_ids=set(registry),
        )
        errors = _validation_errors(
            card_effect.path,
            card_effect.present,
            card_effect.errors,
        )
        payload["card_effect_evidence_manifest"] = card_effect.to_payload()
        payload["card_effect_evidence_manifest_errors"] = errors
        coverage = card_effect_evidence_coverage(card_effect_path)
        payload["card_effect_evidence_coverage"] = coverage.to_payload()
        payload["card_effect_evidence_target_details"] = card_effect_target_details(
            coverage
        )
        payload["ok"] = payload["ok"] and not errors
    if expansion_composition_path is not None:
        expansion = validate_expansion_composition_evidence_manifest(
            expansion_composition_path
        )
        errors = _validation_errors(expansion.path, expansion.present, expansion.errors)
        payload["expansion_composition_evidence_manifest"] = expansion.to_payload()
        payload["expansion_composition_evidence_manifest_errors"] = errors
        coverage = expansion_composition_evidence_coverage(expansion_composition_path)
        payload["expansion_composition_evidence_coverage"] = coverage.to_payload()
        payload["expansion_composition_evidence_target_details"] = (
            expansion_composition_target_details(coverage)
        )
        payload["ok"] = payload["ok"] and not errors
    return payload


def _validation_errors(
    path: Path,
    present: bool,
    errors: list[dict[str, str]],
) -> list[dict[str, str]]:
    if not present:
        return [{"path": str(path), "error": "missing_manifest"}]
    return errors


__all__ = ["validate_source_evidence_files"]
