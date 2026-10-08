"""Known edition and variant boundaries."""

from __future__ import annotations

from dataclasses import dataclass

from .variant_acceptance import VARIANT_ACCEPTANCE_CRITERIA
from .variants import ACTIVE_VARIANT, ACTIVE_VARIANT_ID, RulesVariant


@dataclass(frozen=True)
class RulesVariantCatalogEntry:
    variant_id: str
    status: str
    source_ids: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "variant_id": self.variant_id,
            "status": self.status,
            "source_ids": list(self.source_ids),
            "acceptance_criteria": list(self.acceptance_criteria),
            "blockers": list(self.blockers),
        }


VARIANT_CATALOG = (
    RulesVariantCatalogEntry(
        ACTIVE_VARIANT_ID,
        "active",
        ("MIR-001", "MIR-002"),
        VARIANT_ACCEPTANCE_CRITERIA[ACTIVE_VARIANT_ID],
        (),
    ),
    RulesVariantCatalogEntry(
        "classic_spinner_scan",
        "deferred",
        ("MIR-002",),
        VARIANT_ACCEPTANCE_CRITERIA["classic_spinner_scan"],
        ("spinner probabilities", "9-card hand model"),
    ),
    RulesVariantCatalogEntry(
        "nuclear_destruction_modern",
        "deferred",
        ("OFF-002", "OFF-003"),
        VARIANT_ACCEPTANCE_CRITERIA["nuclear_destruction_modern"],
        ("ND deck composition", "Nuclear Escalation die"),
    ),
    RulesVariantCatalogEntry(
        "postal_press",
        "deferred",
        ("UNOFF-001",),
        VARIANT_ACCEPTANCE_CRITERIA["postal_press"],
        ("press adjudication", "simultaneous orders"),
    ),
    RulesVariantCatalogEntry(
        "no_press_house",
        "deferred",
        ("UNOFF-001",),
        VARIANT_ACCEPTANCE_CRITERIA["no_press_house"],
        ("house-mode boundary",),
    ),
    RulesVariantCatalogEntry(
        "combined_expansions",
        "deferred",
        ("OFF-002", "OFF-003", "COMM-002", "COMM-004", "COMM-005"),
        VARIANT_ACCEPTANCE_CRITERIA["combined_expansions"],
        ("authorized expansion composition", "exact card text"),
    ),
)


def variant_catalog_payload() -> list[dict[str, object]]:
    return [entry.to_payload() for entry in VARIANT_CATALOG]


def known_variant_ids() -> tuple[str, ...]:
    return tuple(entry.variant_id for entry in VARIANT_CATALOG)


def variant_catalog_gaps(source_ids: set[str]) -> list[dict[str, str]]:
    gaps = [
        {"variant_id": entry.variant_id, "source_id": source_id}
        for entry in VARIANT_CATALOG
        for source_id in entry.source_ids
        if source_id not in source_ids
    ]
    active = [entry.variant_id for entry in VARIANT_CATALOG if entry.status == "active"]
    if active != [ACTIVE_VARIANT_ID]:
        gaps.append({"variant_id": ACTIVE_VARIANT_ID, "source_id": "active entry"})
    return gaps


def validate_requested_variant(variant_id: object, context: str) -> None:
    resolve_requested_variant(variant_id, context)


def resolve_requested_variant(variant_id: object, context: str) -> RulesVariant:
    if not isinstance(variant_id, str):
        raise ValueError(f"{context} variant_id must be a string")
    entry = _catalog_entry(variant_id)
    if entry is None:
        raise ValueError(f"Unknown variant: {variant_id}")
    if entry.status == "active":
        return ACTIVE_VARIANT
    blockers = ", ".join(entry.blockers)
    raise ValueError(f"{context} variant {variant_id} is deferred: {blockers}")


def _catalog_entry(variant_id: str) -> RulesVariantCatalogEntry | None:
    return next(
        (entry for entry in VARIANT_CATALOG if entry.variant_id == variant_id),
        None,
    )


__all__ = [
    "RulesVariantCatalogEntry",
    "known_variant_ids",
    "resolve_requested_variant",
    "validate_requested_variant",
    "variant_catalog_gaps",
    "variant_catalog_payload",
]
