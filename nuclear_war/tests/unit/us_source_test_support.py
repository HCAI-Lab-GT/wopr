"""Fixtures for U.S. Charter source-register tests."""

from __future__ import annotations

from typing import Any


def minimal_source_register() -> dict[str, Any]:
    return {
        "schema_version": "us-source-register.v0.1",
        "register_id": "US_PUBLIC_2026Q3.sources",
        "register_version": "0.1.0",
        "status": "candidate",
        "snapshot_date": "2026-08-26",
        "sources": [
            {
                "source_id": "SRC_NSC_STATUTE",
                "issuing_institution": "Office of the Law Revision Counsel",
                "public_title": "50 U.S.C. 3021, National Security Council",
                "canonical_url": "https://uscode.house.gov/",
                "publication_date": None,
                "effective_date": None,
                "retrieval_date": "2026-08-26",
                "source_type": "statute",
                "claim_paraphrase": "The Council advises the President.",
                "applicable_office_ids": ["SEAT_PRESIDENT"],
                "applicable_process_ids": ["PROCESS_NSC"],
                "evidence_status": "fact",
                "fact_ids": ["FACT_NSC_ADVISES"],
                "inference_ids": ["INF_TEST_OBJECTIVE"],
            }
        ],
        "facts": [
            {
                "fact_id": "FACT_NSC_ADVISES",
                "statement": "The NSC advises the President.",
                "source_ids": ["SRC_NSC_STATUTE"],
                "office_ids": ["SEAT_PRESIDENT"],
                "process_ids": ["PROCESS_NSC"],
            }
        ],
        "inferences": [
            {
                "inference_id": "INF_TEST_OBJECTIVE",
                "statement": "The test objective is an exercise abstraction.",
                "source_ids": ["SRC_NSC_STATUTE"],
                "fact_ids": ["FACT_NSC_ADVISES"],
                "scope_ids": ["OBJ_PROTECT_US"],
            }
        ],
        "gaps": [],
    }


__all__ = ["minimal_source_register"]
