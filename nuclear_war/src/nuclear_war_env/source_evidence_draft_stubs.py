"""Public-safe draft source evidence stub export."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Literal, TypedDict

from .source_evidence_targets import source_evidence_targets_payload

DraftStubKind = Literal["card-effects", "expansion-composition"]


class CardEffectDraftStub(TypedDict):
    card_id: str
    card_name: str
    card_type: str
    count: int
    effect_summary: str
    evidence_kind: str
    source_photo_or_file: str
    verification_status: str
    verified_by_second_pass: bool


class ExpansionCompositionDraftStub(TypedDict):
    registry_id: str
    card_name: str
    expansion_set: str
    count_in_deck: int
    evidence_kind: str
    source_reference: str
    verification_status: str
    verified_by_second_pass: bool


def card_effect_draft_stubs() -> list[CardEffectDraftStub]:
    return [
        {
            "card_id": target["card_id"],
            "card_name": target["card_name"],
            "card_type": target["card_type"],
            "count": target["count"],
            "effect_summary": "TODO derived effect summary",
            "evidence_kind": "physical_copy",
            "source_photo_or_file": _private_reference(target["card_id"], "jpg"),
            "verification_status": "draft",
            "verified_by_second_pass": False,
        }
        for target in source_evidence_targets_payload()["card_effect_targets"]
    ]


def expansion_composition_draft_stubs() -> list[ExpansionCompositionDraftStub]:
    return [
        {
            "registry_id": target["registry_id"],
            "card_name": _display_name(target["postal_effect"]),
            "expansion_set": "TODO expansion set from source",
            "count_in_deck": 1,
            "evidence_kind": "physical_copy",
            "source_reference": _private_reference(target["registry_id"], "csv"),
            "verification_status": "draft",
            "verified_by_second_pass": False,
        }
        for target in source_evidence_targets_payload()["expansion_composition_targets"]
    ]


def card_effect_draft_stub_jsonl() -> str:
    return _jsonl(card_effect_draft_stubs())


def expansion_composition_draft_stub_jsonl() -> str:
    return _jsonl(expansion_composition_draft_stubs())


def draft_stub_jsonl(kind: DraftStubKind) -> str:
    if kind == "card-effects":
        return card_effect_draft_stub_jsonl()
    return expansion_composition_draft_stub_jsonl()


def _jsonl(records: Sequence[object]) -> str:
    return "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n"


def _private_reference(item_id: str, suffix: str) -> str:
    return f"private/source-capture/{item_id}.{suffix}"


def _display_name(value: str) -> str:
    return value.replace("_", " ").title()


__all__ = [
    "CardEffectDraftStub",
    "DraftStubKind",
    "ExpansionCompositionDraftStub",
    "card_effect_draft_stub_jsonl",
    "card_effect_draft_stubs",
    "draft_stub_jsonl",
    "expansion_composition_draft_stub_jsonl",
    "expansion_composition_draft_stubs",
]
