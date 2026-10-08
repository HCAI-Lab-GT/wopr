"""LLM agent table harness integration tests."""

from __future__ import annotations

from nuclear_war_agents import (
    LLMDecisionAgent,
    ObservationHeuristicAgent,
    ScriptedLLMClient,
    TraceRecorder,
)
from nuclear_war_env.replay_validation import validate_replay_payload
from nuclear_war_env.simulation import (
    SimulationConfig,
    run_table_simulation_with_decision_agents,
)


def test_mixed_table_simulation_records_llm_traces() -> None:
    recorder = TraceRecorder()
    agents = {
        "player_0": LLMDecisionAgent(
            ScriptedLLMClient(['{"action_id": "player_0:draw"}']),
            recorder=recorder,
        ),
        "player_1": ObservationHeuristicAgent(),
        "player_2": ObservationHeuristicAgent(),
    }

    result = run_table_simulation_with_decision_agents(
        SimulationConfig(
            mode="table",
            players=3,
            seed=7,
            agent="decision_heuristic",
            max_turns=1,
        ),
        agents,
    )

    validate_replay_payload(result)
    action_ids = {action["action_id"] for action in result["actions"]}
    assert recorder.traces
    assert recorder.traces[0].selected_action_id in action_ids
    assert recorder.traces[0].player_id == "player_0"
    assert recorder.traces[0].decision_type
