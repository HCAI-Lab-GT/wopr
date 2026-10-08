"""Fixtures for U.S. Room Charter tests."""

from __future__ import annotations

from typing import Any


def minimal_us_charter(source_hash: str) -> dict[str, Any]:
    fact_ids = ["FACT_NSC_ADVISES"]
    predicate_id = "ACT_ALWAYS"
    product_id = "PRODUCT_OPTIONS"
    return {
        "schema_version": "us-room-charter.v0.1",
        "charter_id": "US_PUBLIC_2026Q3",
        "charter_version": "0.1.0",
        "status": "candidate",
        "source_register_id": "US_PUBLIC_2026Q3.sources",
        "source_register_hash": source_hash,
        "actor_id": "USA",
        "objective_ids": ["OBJ_PROTECT_US"],
        "institution_registry": {
            "seats": [
                {
                    "seat_id": "SEAT_PRESIDENT",
                    "office_class": "President",
                    "first_slice_disposition": "active",
                    "adviser_status": "voting_principal",
                    "mandate": "Decide presidential policy.",
                    "supported_contributions": ["policy_decision"],
                    "prohibited_actions": ["world_mutation"],
                    "information_entitlement_ids": ["INFO_COMMON"],
                    "group_ids": ["GROUP_NSC"],
                    "activation_predicate_ids": [predicate_id],
                    "decision_route_roles": ["owning_authority"],
                    "persona_posture_ids": [],
                    "represented_role_ids": [],
                    "fact_ids": fact_ids,
                    "inference_ids": [],
                }
            ],
            "services": [
                {
                    "service_id": "SERVICE_WATCH",
                    "purpose": "Deliver authorized records without interpretation.",
                    "responsibilities": ["delivery"],
                    "prohibited_actions": ["summarization"],
                    "activation_predicate_ids": [predicate_id],
                    "fact_ids": [],
                    "inference_ids": [],
                }
            ],
        },
        "groups": [
            {
                "group_id": "GROUP_NSC",
                "purpose": "Advise the President.",
                "ordered_eligible_member_ids": ["SEAT_PRESIDENT"],
                "active_member_rule": "all_activated",
                "input_entitlement_ids": ["INFO_COMMON"],
                "dependency_group_ids": [],
                "shared_seat_barrier_ids": [],
                "activation_predicate_id": predicate_id,
                "product_schema_id": product_id,
                "collection_order": 0,
                "failure_effect": "incomplete_route",
                "fact_ids": fact_ids,
                "inference_ids": [],
            }
        ],
        "information_classes": [
            {
                "information_class_id": "INFO_COMMON",
                "description": "Common Crisis Picture.",
                "sensitivity": "common",
                "fact_ids": [],
                "inference_ids": [],
            }
        ],
        "disclosure_permissions": [],
        "activation_predicates": [
            {
                "activation_predicate_id": predicate_id,
                "predicate_type": "always",
                "condition_ids": [],
                "first_episode_value": True,
                "description": "Always active.",
                "fact_ids": [],
                "inference_ids": [],
            }
        ],
        "decision_routes": [
            {
                "route_id": "ROUTE_PRESIDENTIAL",
                "action_class": "presidential_policy",
                "applicability_predicate_id": predicate_id,
                "owning_authority_seat_id": "SEAT_PRESIDENT",
                "eligible_forum_group_id": "GROUP_NSC",
                "decision_rule": "president_decides",
                "presidential_attention_rule": "required",
                "consultation_group_ids": [],
                "required_confirmation_ids": [],
                "final_decision_record_schema_id": product_id,
                "failure_effect": "no_supported_decision",
                "fact_ids": fact_ids,
                "inference_ids": [],
            }
        ],
        "required_confirmations": [],
        "product_schemas": [
            {
                "product_schema_id": product_id,
                "product_type": "options",
                "producing_group_ids": ["GROUP_NSC"],
                "required_fields": ["options"],
                "preserves_dissent": True,
                "fact_ids": [],
                "inference_ids": [],
            }
        ],
        "evidence_labels": [
            {
                "evidence_label_id": "EVIDENCE_FACT",
                "label": "FACT",
                "description": "Public-source fact.",
            }
        ],
    }


__all__ = ["minimal_us_charter"]
