"""Rules trace coverage against table replay records."""

from __future__ import annotations

from nuclear_war_env.rules_trace import rules_trace_payload, rules_trace_step_payload
from nuclear_war_env.rules_trace_replay import rules_trace_replay_payload
from nuclear_war_env.simulation import SimulationConfig, run_simulation


def test_rules_trace_covers_representative_table_replay_records() -> None:
    result = run_simulation(
        SimulationConfig(
            mode="table",
            players=3,
            seed=3,
            agent="heuristic",
            max_turns=100,
        )
    )
    trace_types = {
        (item["record_kind"], item["record_type"]) for item in rules_trace_payload()
    }
    replay_types = {
        ("action", action["action_type"]) for action in result["actions"]
    } | {("event", event["event_type"]) for event in result["events"]}

    assert replay_types <= trace_types


def test_rules_trace_replay_records_use_known_rule_steps() -> None:
    step_ids = {item["step_id"] for item in rules_trace_step_payload()}
    trace_steps = {item["rule_step"] for item in rules_trace_payload()}

    assert trace_steps <= step_ids


def test_rules_trace_maps_full_table_game_to_source_backed_steps() -> None:
    result = run_simulation(
        SimulationConfig(
            mode="table",
            players=3,
            seed=1,
            agent="heuristic",
            max_turns=100,
        )
    )

    trace = rules_trace_replay_payload(result)
    step_ids = {item["step_id"] for item in rules_trace_step_payload()}

    # Seed 1 ends in mutual annihilation since the 2026-07-02 final-retaliation
    # pool fix; the semantic trace must still cover every record.
    assert result["termination_reason"] == "no_players_remaining"
    assert len(trace) == len(result["actions"]) + len(result["events"])
    assert {entry["rule_step"] for entry in trace} <= step_ids
    assert all(entry["status"] == "semantic_mapped" for entry in trace)
    assert all(entry["source_ids"] for entry in trace)
