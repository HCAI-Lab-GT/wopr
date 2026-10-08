"""Public-safe source evidence target detail filtering."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from .source_evidence_coverage import SourceEvidenceCoverage
from .source_evidence_targets import (
    CardEffectTarget,
    ExpansionCompositionTarget,
    source_evidence_targets_payload,
)


class CardEffectTargetDetails(TypedDict):
    missing_targets: list[CardEffectTarget]
    unverified_targets: list[CardEffectTarget]


class ExpansionCompositionTargetDetails(TypedDict):
    missing_targets: list[ExpansionCompositionTarget]
    unverified_targets: list[ExpansionCompositionTarget]


def card_effect_target_details(
    coverage: SourceEvidenceCoverage,
    registry_path: Path | None = None,
) -> CardEffectTargetDetails:
    payload = (
        source_evidence_targets_payload()
        if registry_path is None
        else source_evidence_targets_payload(registry_path)
    )
    targets = {target["card_id"]: target for target in payload["card_effect_targets"]}
    return {
        "missing_targets": _select_card_targets(coverage.missing_ids(), targets),
        "unverified_targets": _select_card_targets(coverage.unverified_ids(), targets),
    }


def expansion_composition_target_details(
    coverage: SourceEvidenceCoverage,
) -> ExpansionCompositionTargetDetails:
    payload = source_evidence_targets_payload()
    targets = {
        target["registry_id"]: target
        for target in payload["expansion_composition_targets"]
    }
    return {
        "missing_targets": _select_expansion_targets(coverage.missing_ids(), targets),
        "unverified_targets": _select_expansion_targets(
            coverage.unverified_ids(), targets
        ),
    }


def _select_card_targets(
    ids: list[str],
    targets: dict[str, CardEffectTarget],
) -> list[CardEffectTarget]:
    return [targets[item] for item in ids if item in targets]


def _select_expansion_targets(
    ids: list[str],
    targets: dict[str, ExpansionCompositionTarget],
) -> list[ExpansionCompositionTarget]:
    return [targets[item] for item in ids if item in targets]


__all__ = [
    "CardEffectTargetDetails",
    "ExpansionCompositionTargetDetails",
    "card_effect_target_details",
    "expansion_composition_target_details",
]
