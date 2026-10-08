from __future__ import annotations

from typing import Any

from nuclear_war_env.llm_trace_artifacts import build_trace_artifact
from nuclear_war_env.observation import observe
from nuclear_war_env.simulation import (
    SimulationConfig,
    run_table_simulation_with_decision_agents,
)

from .c2_artifacts import build_c2_artifact
from .call_budget import ChannelCallBudget, ChannelRequestBudgetExceeded
from .config import ConcordiaNoPressConfig
from .failure import ConcordiaDecisionFailure
from .harness_agents import build_seat_runtimes
from .harness_failure import budget_failure, build_run_failure
from .harness_payloads import (
    agent_metadata,
    config_snapshot,
    runtime_payload,
    summary,
)
from .harness_press import build_press_coordinator
from .harness_runtime import execution_runtime_path
from .press_artifacts import build_press_artifact
from .press_visibility import visible_to
from .runtime import detect_concordia_runtime

_NATIVE_AGENTS = {"concordia_native_first_legal", "concordia_native_http"}
_PRESS_ENABLED_MODES = {"press_light", "multi_turn_public", "full_press"}


def _reject_native_press_seats(config: ConcordiaNoPressConfig) -> None:
    native = sorted(
        pid for pid, seat in config.seats.items() if seat.agent in _NATIVE_AGENTS
    )
    if native:
        raise ValueError(
            "Concordia press is not supported for native seats "
            f"{native}; HTTP remains the press producer"
        )


def run_concordia_no_press_game(
    config: ConcordiaNoPressConfig,
    call_budget: ChannelCallBudget | None = None,
) -> dict[str, Any]:
    press_enabled = config.press.enabled and config.press.mode in _PRESS_ENABLED_MODES
    if press_enabled:
        _reject_native_press_seats(config)
    detected_runtime = detect_concordia_runtime()
    runtime_path = execution_runtime_path(config, detected_runtime)
    traces: list[dict[str, Any]] = []
    press_traces: list[dict[str, Any]] = []
    runtimes = build_seat_runtimes(config, traces, runtime_path, call_budget)
    agents = {
        player_id: runtime.strategic_agent for player_id, runtime in runtimes.items()
    }
    coordinator = (
        build_press_coordinator(config, runtimes, press_traces)
        if press_enabled
        else None
    )
    press_memory: list[dict[str, Any]] = []

    def press_hook(state, completed_round: int) -> None:
        if coordinator is None:
            return
        living = [pid for pid in state.players if state.players[pid].alive]
        observations = {pid: observe(state, pid) for pid in living}
        log = coordinator.run_round_press(
            observations=observations,
            round_no=completed_round + 1,
        )
        press_memory.extend(log)
        for player_id, runtime in runtimes.items():
            runtime.set_press_memory(visible_to(player_id, press_memory))

    try:
        replay = run_table_simulation_with_decision_agents(
            SimulationConfig(
                mode="table",
                players=config.players,
                seed=config.seed,
                # Per-seat Concordia agents drive every seat, so the replay's
                # single-agent label is honestly "mixed_seats" (the authoritative
                # per-seat mapping lives in agent_metadata / config_snapshot).
                agent="mixed_seats",
                max_turns=config.max_turns,
                press=False,
                variant_id=config.variant_id,
            ),
            agents,
            press_hook=press_hook if press_enabled else None,
        )
    except ChannelRequestBudgetExceeded as exc:
        failure = build_run_failure(
            config,
            detected_runtime,
            runtime_path,
            runtimes,
            budget_failure(exc),
            channel_metrics=call_budget.snapshot() if call_budget else None,
        )
        raise failure from exc
    except ConcordiaDecisionFailure as exc:
        failure = build_run_failure(
            config,
            detected_runtime,
            runtime_path,
            runtimes,
            exc,
            channel_metrics=call_budget.snapshot() if call_budget else None,
        )
        raise failure from exc
    c2_artifact = build_c2_artifact(replay, runtimes)
    result = {
        "replay": replay,
        "trace_artifact": build_trace_artifact(replay, traces),
        "c2_artifact": c2_artifact,
        "runtime": runtime_payload(detected_runtime, runtime_path),
        "agent_metadata": agent_metadata(config),
        "config_snapshot": config_snapshot(config),
        "summary": summary(
            replay,
            traces,
            runtime_path,
            len(press_traces),
            c2_artifact=c2_artifact,
            press_traces=press_traces,
            budget_metrics=call_budget.snapshot() if call_budget else None,
        ),
    }
    if press_enabled:
        result["press_artifact"] = build_press_artifact(
            replay, press_traces, config.press.mode
        )
    return result
