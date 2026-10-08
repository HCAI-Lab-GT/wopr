"""Semantic rules trace over replay payloads."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from .rules_trace import RULES_TRACE, RulesTraceRecord
from .rules_trace_steps import RuleStep, rules_trace_steps_by_id

FULL_GAME_TRACE_CONFIG = {
    "mode": "table",
    "players": 3,
    "seed": 1,
    "agent": "heuristic",
    "max_turns": 100,
}


@dataclass(frozen=True)
class RulesTraceReplayEntry:
    sequence: int
    turn: int
    record_kind: str
    record_type: str
    trace_id: str
    rule_step: str
    rule_area: str
    source_ids: tuple[str, ...]
    status: str = "semantic_mapped"

    def to_payload(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "turn": self.turn,
            "record_kind": self.record_kind,
            "record_type": self.record_type,
            "trace_id": self.trace_id,
            "rule_step": self.rule_step,
            "rule_area": self.rule_area,
            "source_ids": list(self.source_ids),
            "status": self.status,
        }


def rules_trace_replay_payload(
    replay_payload: dict[str, Any],
) -> list[dict[str, object]]:
    trace_records = _trace_records_by_kind_type()
    steps = rules_trace_steps_by_id()
    gaps = rules_trace_replay_gaps(replay_payload)
    if gaps:
        raise ValueError(f"Replay contains unmapped rules trace records: {gaps}")
    entries: list[RulesTraceReplayEntry] = []
    for sequence, record in enumerate(_ordered_replay_records(replay_payload), 1):
        turn, record_kind, record_type = record
        trace_record = trace_records[(record_kind, record_type)]
        step = steps[trace_record.rule_step]
        entries.append(_entry(sequence, turn, trace_record, step))
    return [entry.to_payload() for entry in entries]


def rules_trace_replay_gaps(replay_payload: dict[str, Any]) -> list[dict[str, str]]:
    trace_records = _trace_records_by_kind_type()
    steps = rules_trace_steps_by_id()
    gaps: list[dict[str, str]] = []
    for turn, record_kind, record_type in _ordered_replay_records(replay_payload):
        trace_record = trace_records.get((record_kind, record_type))
        if trace_record is None:
            gaps.append(
                {
                    "record_kind": record_kind,
                    "record_type": record_type,
                    "turn": str(turn),
                }
            )
            continue
        if trace_record.rule_step not in steps:
            gaps.append(
                {
                    "trace_id": trace_record.trace_id,
                    "rule_step": trace_record.rule_step,
                    "turn": str(turn),
                }
            )
    return gaps


def rules_trace_full_game_summary() -> dict[str, object]:
    summary, _gaps = _full_game_trace_result()
    return dict(summary)


def rules_trace_full_game_gaps() -> list[dict[str, str]]:
    _summary, gaps = _full_game_trace_result()
    return [dict(gap) for gap in gaps]


@lru_cache(maxsize=1)
def _full_game_trace_result() -> tuple[dict[str, object], tuple[dict[str, str], ...]]:
    from .simulation import SimulationConfig, run_simulation

    result = run_simulation(SimulationConfig(**FULL_GAME_TRACE_CONFIG))
    gaps = rules_trace_replay_gaps(result)
    trace_entry_count = 0 if gaps else len(rules_trace_replay_payload(result))
    summary: dict[str, object] = {
        "mode": FULL_GAME_TRACE_CONFIG["mode"],
        "players": FULL_GAME_TRACE_CONFIG["players"],
        "seed": FULL_GAME_TRACE_CONFIG["seed"],
        "agent": FULL_GAME_TRACE_CONFIG["agent"],
        "turns": result["turns"],
        "termination_reason": result["termination_reason"],
        "action_count": len(result["actions"]),
        "event_count": len(result["events"]),
        "trace_entry_count": trace_entry_count,
        "gap_count": len(gaps),
    }
    return summary, tuple(gaps)


def _entry(
    sequence: int,
    turn: int,
    trace_record: RulesTraceRecord,
    step: RuleStep,
) -> RulesTraceReplayEntry:
    return RulesTraceReplayEntry(
        sequence=sequence,
        turn=turn,
        record_kind=trace_record.record_kind,
        record_type=trace_record.record_type,
        trace_id=trace_record.trace_id,
        rule_step=trace_record.rule_step,
        rule_area=step.rule_area,
        source_ids=tuple(dict.fromkeys((*trace_record.source_ids, *step.source_ids))),
    )


def _ordered_replay_records(
    replay_payload: dict[str, Any],
) -> list[tuple[int, str, str]]:
    actions = [
        (int(action["turn"]), index, "action", str(action["action_type"]))
        for index, action in enumerate(replay_payload.get("actions", []))
    ]
    events = [
        (int(event["turn"]), index, "event", str(event["event_type"]))
        for index, event in enumerate(replay_payload.get("events", []))
    ]
    ordered = sorted(actions + events, key=lambda item: (item[0], item[2], item[1]))
    return [
        (turn, record_kind, record_type)
        for turn, _index, record_kind, record_type in ordered
    ]


def _trace_records_by_kind_type() -> dict[tuple[str, str], RulesTraceRecord]:
    return {(record.record_kind, record.record_type): record for record in RULES_TRACE}


__all__ = [
    "FULL_GAME_TRACE_CONFIG",
    "RulesTraceReplayEntry",
    "rules_trace_full_game_gaps",
    "rules_trace_full_game_summary",
    "rules_trace_replay_gaps",
    "rules_trace_replay_payload",
]
