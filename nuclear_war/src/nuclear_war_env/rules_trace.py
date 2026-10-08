"""Source-linked replay trace scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from .rules_trace_catalog import TRACE_ROWS
from .rules_trace_steps import (
    rules_trace_step_ids,
    rules_trace_step_payload,
    rules_trace_step_source_gaps,
)


@dataclass(frozen=True)
class RulesTraceRecord:
    trace_id: str
    record_kind: str
    record_type: str
    rule_step: str
    source_ids: tuple[str, ...]
    status: str = "scaffolded"

    def to_payload(self) -> dict[str, object]:
        return {
            "trace_id": self.trace_id,
            "record_kind": self.record_kind,
            "record_type": self.record_type,
            "rule_step": self.rule_step,
            "source_ids": list(self.source_ids),
            "status": self.status,
        }


RULES_TRACE = tuple(RulesTraceRecord(*row) for row in TRACE_ROWS)


def rules_trace_payload() -> list[dict[str, object]]:
    return [record.to_payload() for record in RULES_TRACE]


def rules_trace_source_gaps(source_ids: set[str]) -> list[dict[str, str]]:
    return [
        {"trace_id": record.trace_id, "source_id": source_id}
        for record in RULES_TRACE
        for source_id in record.source_ids
        if source_id not in source_ids
    ]


def rules_trace_step_gaps() -> list[dict[str, str]]:
    step_ids = rules_trace_step_ids()
    return [
        {"trace_id": record.trace_id, "rule_step": record.rule_step}
        for record in RULES_TRACE
        if record.rule_step not in step_ids
    ]


__all__ = [
    "RULES_TRACE",
    "RulesTraceRecord",
    "rules_trace_payload",
    "rules_trace_step_gaps",
    "rules_trace_step_payload",
    "rules_trace_step_source_gaps",
    "rules_trace_source_gaps",
]
