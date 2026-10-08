"""Source-mapped rules trace steps."""

from __future__ import annotations

from dataclasses import dataclass

from .rules_trace_step_catalog import RULE_STEP_ROWS


@dataclass(frozen=True)
class RuleStep:
    step_id: str
    rule_area: str
    summary: str
    source_ids: tuple[str, ...]
    status: str = "source_mapped"

    def to_payload(self) -> dict[str, object]:
        return {
            "step_id": self.step_id,
            "rule_area": self.rule_area,
            "summary": self.summary,
            "source_ids": list(self.source_ids),
            "status": self.status,
        }


RULES_TRACE_STEPS = tuple(RuleStep(*row) for row in RULE_STEP_ROWS)


def rules_trace_step_ids() -> set[str]:
    return {step.step_id for step in RULES_TRACE_STEPS}


def rules_trace_steps_by_id() -> dict[str, RuleStep]:
    return {step.step_id: step for step in RULES_TRACE_STEPS}


def rules_trace_step_payload() -> list[dict[str, object]]:
    return [step.to_payload() for step in RULES_TRACE_STEPS]


def rules_trace_step_source_gaps(source_ids: set[str]) -> list[dict[str, str]]:
    return [
        {"step_id": step.step_id, "source_id": source_id}
        for step in RULES_TRACE_STEPS
        for source_id in step.source_ids
        if source_id not in source_ids
    ]


__all__ = [
    "RULES_TRACE_STEPS",
    "RuleStep",
    "rules_trace_step_ids",
    "rules_trace_step_payload",
    "rules_trace_step_source_gaps",
    "rules_trace_steps_by_id",
]
