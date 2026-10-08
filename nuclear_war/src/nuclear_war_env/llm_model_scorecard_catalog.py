"""Catalog-only predicted scorecards for serverless chat models."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelCatalogRow:
    model_id: str
    name: str
    context: int | None
    input_price: float | None
    cached_input_price: float | None
    output_price: float | None
    quantization: str | None
    function_calling: str | None
    structured_outputs: str | None


@dataclass(frozen=True)
class CatalogScore:
    model_id: str
    score_type: str
    total_score: float
    cost_score: float
    context_score: float
    interface_score: float
    risk_flags: tuple[str, ...]


def load_catalog_rows(path: Path) -> list[ModelCatalogRow]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [_row_from_payload(item) for item in payload["chat"]]


def score_catalog_row(row: ModelCatalogRow) -> CatalogScore:
    risk_flags = _risk_flags(row)
    cost_score = _cost_score(row)
    context_score = _context_score(row)
    interface_score = _interface_score(row)
    total_score = cost_score + context_score + interface_score - len(risk_flags) * 5
    return CatalogScore(
        model_id=row.model_id,
        score_type="predicted",
        total_score=total_score,
        cost_score=cost_score,
        context_score=context_score,
        interface_score=interface_score,
        risk_flags=tuple(risk_flags),
    )


def score_catalog_rows(rows: Sequence[ModelCatalogRow]) -> list[CatalogScore]:
    return [score_catalog_row(row) for row in rows]


def _row_from_payload(payload: dict[str, object]) -> ModelCatalogRow:
    return ModelCatalogRow(
        model_id=str(payload["id"]),
        name=str(payload["name"]),
        context=_optional_int(payload.get("context"), "context"),
        input_price=_optional_float(payload.get("input"), "input"),
        cached_input_price=_optional_float(payload.get("cached_input"), "cached_input"),
        output_price=_optional_float(payload.get("output"), "output"),
        quantization=_optional_text(payload.get("quantization")),
        function_calling=_optional_text(payload.get("function_calling")),
        structured_outputs=_optional_text(payload.get("structured_outputs")),
    )


def _risk_flags(row: ModelCatalogRow) -> list[str]:
    flags = []
    if row.context is not None and row.context < 32768:
        flags.append("context_under_32768")
    if row.structured_outputs != "yes":
        flags.append("missing_structured_outputs")
    if row.function_calling != "yes":
        flags.append("missing_function_calling")
    return flags


def _cost_score(row: ModelCatalogRow) -> float:
    input_price = row.input_price or 0.0
    output_price = row.output_price or 0.0
    cached_input_price = (
        input_price if row.cached_input_price is None else row.cached_input_price
    )
    return 100.0 - (input_price * 25.0 + output_price * 35.0 + cached_input_price * 5.0)


def _context_score(row: ModelCatalogRow) -> float:
    if row.context is None:
        return 0.0
    return min(row.context, 262144) / 2048.0


def _interface_score(row: ModelCatalogRow) -> float:
    score = 0.0
    if row.function_calling == "yes":
        score += 12.0
    if row.structured_outputs == "yes":
        score += 18.0
    return score


def _catalog_numeric_value(value: object, field_name: str) -> str | int | float | None:
    if value is None or isinstance(value, str | int | float):
        return value
    raise ValueError(
        f"Catalog numeric field {field_name} must be str, int, float, or None; "
        f"got {type(value).__name__}"
    )


def _optional_int(value: object, field_name: str) -> int | None:
    numeric_value = _catalog_numeric_value(value, field_name)
    return None if numeric_value is None else int(numeric_value)


def _optional_float(value: object, field_name: str) -> float | None:
    numeric_value = _catalog_numeric_value(value, field_name)
    return None if numeric_value is None else float(numeric_value)


def _optional_text(value: object) -> str | None:
    return None if value is None else str(value)


__all__ = [
    "CatalogScore",
    "ModelCatalogRow",
    "load_catalog_rows",
    "score_catalog_row",
    "score_catalog_rows",
]
