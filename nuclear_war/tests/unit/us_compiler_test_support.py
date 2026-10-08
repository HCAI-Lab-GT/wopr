"""Compiled U.S. Charter fixture."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from tests.unit.us_charter_test_support import minimal_us_charter


def _seat(
    seat_id: str, adviser_status: str, group_ids: list[str], entitlements: list[str]
) -> dict[str, Any]:
    return {
        "seat_id": seat_id,
        "office_class": seat_id.removeprefix("SEAT_").title(),
        "first_slice_disposition": "active",
        "adviser_status": adviser_status,
        "mandate": "Supply the declared institutional contribution.",
        "supported_contributions": ["advice"],
        "prohibited_actions": ["world_mutation"],
        "information_entitlement_ids": entitlements,
        "group_ids": group_ids,
        "activation_predicate_ids": ["ACT_ALWAYS"],
        "decision_route_roles": [],
        "persona_posture_ids": [],
        "represented_role_ids": [],
        "fact_ids": ["FACT_NSC_ADVISES"],
        "inference_ids": [],
    }


def _group(group_id: str, member_ids: list[str], product_id: str) -> dict[str, Any]:
    return {
        "group_id": group_id,
        "purpose": "Produce one attributable product.",
        "ordered_eligible_member_ids": member_ids,
        "active_member_rule": "activated_voting_and_advisers",
        "input_entitlement_ids": ["INFO_COMMON"],
        "dependency_group_ids": [],
        "shared_seat_barrier_ids": [],
        "activation_predicate_id": "ACT_ALWAYS",
        "product_schema_id": product_id,
        "collection_order": 0,
        "failure_effect": "incomplete_route",
        "fact_ids": ["FACT_NSC_ADVISES"],
        "inference_ids": [],
    }


def _product(product_id: str, group_id: str) -> dict[str, Any]:
    return {
        "product_schema_id": product_id,
        "product_type": "analysis",
        "producing_group_ids": [group_id],
        "required_fields": ["assessment"],
        "preserves_dissent": True,
        "fact_ids": [],
        "inference_ids": [],
    }


def compilable_us_charter(source_hash: str) -> dict[str, Any]:
    payload = deepcopy(minimal_us_charter(source_hash))
    seats = payload["institution_registry"]["seats"]
    seats[0]["group_ids"] = ["GROUP_NSC"]
    seats.extend(
        [
            _seat(
                "SEAT_DNI",
                "non_voting_adviser",
                ["GROUP_NSC", "GROUP_INTEL"],
                ["INFO_COMMON", "INFO_PRIVATE"],
            ),
            _seat(
                "SEAT_STATE",
                "voting_principal",
                ["GROUP_DIPLOMACY"],
                ["INFO_COMMON"],
            ),
        ]
    )
    payload["groups"][0]["ordered_eligible_member_ids"] = [
        "SEAT_PRESIDENT",
        "SEAT_DNI",
    ]
    payload["groups"][0]["shared_seat_barrier_ids"] = ["SEAT_DNI"]
    payload["groups"].extend(
        [
            _group("GROUP_INTEL", ["SEAT_DNI"], "PRODUCT_INTEL"),
            _group("GROUP_DIPLOMACY", ["SEAT_STATE"], "PRODUCT_DIPLOMACY"),
        ]
    )
    payload["groups"][1]["shared_seat_barrier_ids"] = ["SEAT_DNI"]
    payload["information_classes"].append(
        {
            "information_class_id": "INFO_PRIVATE",
            "description": "Seat-private synthetic fact.",
            "sensitivity": "seat_private",
            "fact_ids": [],
            "inference_ids": [],
        }
    )
    payload["disclosure_permissions"].append(
        {
            "permission_id": "PERMISSION_PRIVATE_DNI",
            "information_class_id": "INFO_PRIVATE",
            "sender_ids": ["SERVICE_WATCH"],
            "recipient_ids": ["SEAT_DNI"],
            "delivery_mode": "direct",
            "fact_ids": [],
            "inference_ids": [],
        }
    )
    payload["product_schemas"].extend(
        [
            _product("PRODUCT_INTEL", "GROUP_INTEL"),
            _product("PRODUCT_DIPLOMACY", "GROUP_DIPLOMACY"),
        ]
    )
    return payload


__all__ = ["compilable_us_charter"]
