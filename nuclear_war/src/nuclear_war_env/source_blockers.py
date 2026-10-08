"""Informational source blockers for remaining fidelity work."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceBlocker:
    blocker_id: str
    category: str
    description: str
    required_evidence: tuple[str, ...]

    def to_payload(self) -> dict[str, object]:
        return {
            "blocker_id": self.blocker_id,
            "category": self.category,
            "description": self.description,
            "required_evidence": list(self.required_evidence),
        }


SOURCE_BLOCKERS = (
    SourceBlocker(
        "card_effect_transcription",
        "card_effects",
        "Exact active-registry card effect values remain unverified.",
        ("physical copy transcription", "second-pass verification"),
    ),
    SourceBlocker(
        "expansion_deck_composition",
        "expansion",
        "Expansion metadata records cannot become playable deck cards yet.",
        ("authorized expansion deck list", "count_in_deck evidence"),
    ),
    SourceBlocker(
        "expansion_rules_verification",
        "expansion",
        "Implemented expansion mechanics need per-mechanic source verification.",
        ("authorized mechanic rules", "replay-valid behavior tests"),
    ),
    SourceBlocker(
        "classic_spinner_edition",
        "variant",
        "Classic spinner edition needs exact randomizer and hand model data.",
        ("spinner probability transcription", "9-card hand source"),
    ),
    SourceBlocker(
        "nuclear_destruction_modern",
        "variant",
        "Nuclear Destruction needs its own edition module before selection.",
        ("ND deck composition", "Escalation die rules", "six-player mat rules"),
    ),
    SourceBlocker(
        "press_adjudication",
        "press",
        "Press remains rejected until communication adjudication is specified.",
        ("press adjudication rules", "simultaneous-order rules"),
    ),
)


def source_blocker_payload() -> list[dict[str, object]]:
    return [blocker.to_payload() for blocker in SOURCE_BLOCKERS]


__all__ = ["SOURCE_BLOCKERS", "SourceBlocker", "source_blocker_payload"]
