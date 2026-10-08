"""Deterministic Nuclear War simulation runner."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from nuclear_war_agents import (
    HeuristicAgent,
    InteractiveAgent,
    ObservationHeuristicAgent,
    RandomAgent,
)

from .actions import apply_action, legal_actions
from .agent_action_validation import require_legal_agent_action
from .agent_names import DECISION_HEURISTIC_AGENT, REPLAY_AGENT_NAMES
from .agent_protocol import DecisionAgent
from .engine import execute_postal_turn
from .replay import action_to_dict, event_to_dict, final_populations
from .rng import SeededRNG
from .setup_game import create_game_state
from .simulation_config_validation import validate_simulation_config
from .simulation_turns import turn_player_ids
from .state import GameState
from .variant_catalog import resolve_requested_variant
from .variants import ACTIVE_VARIANT_ID

PressHook = Callable[["GameState", int], None]


@dataclass(frozen=True)
class SimulationConfig:
    mode: str
    players: int
    seed: int
    agent: str
    max_turns: int = 50
    press: bool = False
    variant_id: str = ACTIVE_VARIANT_ID


LegacySimulationAgent = RandomAgent | HeuristicAgent | InteractiveAgent
SimulationAgent = LegacySimulationAgent | ObservationHeuristicAgent


def run_simulation(config: SimulationConfig) -> dict[str, Any]:
    validate_simulation_config(
        config.mode,
        config.players,
        config.seed,
        config.agent,
        config.max_turns,
        config.press,
        config.variant_id,
    )
    state = _create_state(config)
    rng = SeededRNG(config.seed)
    agent = _build_agent(config.agent, rng)
    actions_log: list[dict[str, Any]] = []
    events_log: list[dict[str, Any]] = []
    if config.mode == "table":
        return _run_table_simulation(config, state, agent, actions_log, events_log)
    postal_agent = _legacy_agent(agent)
    for turn in range(1, config.max_turns + 1):
        state.turn = turn
        for player_id in turn_player_ids(state):
            player = state.players[player_id]
            if not player.alive and not player.pending_orders.get("final_strike"):
                continue
            actions = legal_actions(state, player_id, config.mode)
            action = require_legal_agent_action(postal_agent.choose(actions), actions)
            actions_log.append(action_to_dict(action, turn))
            events_log.extend(
                event_to_dict(event, turn) for event in apply_action(state, action)
            )
        if config.mode == "postal":
            events_log.extend(
                event_to_dict(event, turn) for event in execute_postal_turn(state)
            )
        reason = _termination_reason(state, turn, config.max_turns)
        if reason:
            return _result(config, state, turn, reason, actions_log, events_log)
    return _result(
        config, state, config.max_turns, "max_turns", actions_log, events_log
    )


def run_table_simulation_with_decision_agents(
    config: SimulationConfig,
    decision_agents: Mapping[str, DecisionAgent],
    press_hook: PressHook | None = None,
) -> dict[str, Any]:
    # Per-seat agents drive this path, so config.agent is a replay label (e.g.
    # "mixed_seats"), not a runnable single agent — validate against the label set.
    validate_simulation_config(
        config.mode,
        config.players,
        config.seed,
        config.agent,
        config.max_turns,
        config.press,
        config.variant_id,
        allowed_agents=REPLAY_AGENT_NAMES,
    )
    if config.mode != "table":
        raise ValueError("Decision-agent injection is table-only")
    state = _create_state(config)
    _validate_decision_agent_seats(state, decision_agents)
    return _run_table_simulation_with_agents(
        config, state, decision_agents, [], [], press_hook
    )


def _run_table_simulation(
    config: SimulationConfig,
    state: GameState,
    agent: SimulationAgent,
    actions_log: list[dict[str, Any]],
    events_log: list[dict[str, Any]],
) -> dict[str, Any]:
    """Drive a table-mode game through the decision loop, preserving parity.

    The loop pauses at the same decision points the legacy table driver consulted
    the agent on, in the same order with the same option lists, so the legacy
    adapter's ``options[0]`` / random pick reproduces today's outcomes. Actions
    and events are logged in order with the round each occurred in (a round is one
    full clockwise pass of the players), matching the old per-round numbering;
    termination is checked once per completed round, exactly as the legacy outer
    loop did, so a game that ends by ``max_turns`` stops on the same round.
    """
    decision_agent = _as_decision_agent(agent)
    decision_agents = {player_id: decision_agent for player_id in state.players}
    return _run_table_simulation_with_agents(
        config,
        state,
        decision_agents,
        actions_log,
        events_log,
        None,
    )


def _run_table_simulation_with_agents(
    config: SimulationConfig,
    state: GameState,
    decision_agents: Mapping[str, DecisionAgent],
    actions_log: list[dict[str, Any]],
    events_log: list[dict[str, Any]],
    press_hook: PressHook | None = None,
) -> dict[str, Any]:
    from .decision_loop import (
        _RoundStamper,
        apply_decision_result,
        at_round_boundary,
        pending_decision,
        resume_round,
        start_game,
    )
    from .observation import observe

    def record(batch: _RoundStamper) -> None:
        # Each entry is paired with the round it occurred in, reproducing the legacy
        # per-round replay turn numbers.
        for action, turn in batch.actions:
            actions_log.append(action_to_dict(action, turn))
        for event, turn in batch.events:
            events_log.append(event_to_dict(event, turn))

    record(start_game(state, stop_at_round_boundary=True))
    while True:
        decision = pending_decision(state)
        if decision is not None:
            decision_agent = decision_agents[decision.agent_id]
            chosen = require_legal_agent_action(
                decision_agent.choose(
                    observe(state, decision.agent_id), decision.options
                ),
                decision.options,
            )
            record(apply_decision_result(state, chosen, stop_at_round_boundary=True))
            continue
        if at_round_boundary(state):
            # A full round just finished (the cursor has rolled into the next round).
            # Check termination exactly once per round, as the legacy outer loop did,
            # before the new round mutates any state.
            assert state.cursor is not None
            completed_round = state.cursor.round - 1
            reason = _termination_reason(state, completed_round, config.max_turns)
            if reason:
                return _result(
                    config, state, completed_round, reason, actions_log, events_log
                )
            if press_hook is not None:
                press_hook(state, completed_round)
            record(resume_round(state, stop_at_round_boundary=True))
            continue
        break  # terminal: fewer than two players survive
    # The loop terminates at a round boundary, where the cursor's round counter has
    # already rolled into the (never-played) next round; the game actually ended in
    # the round just completed.
    final_round = max(1, (state.cursor.round - 1) if state.cursor else 1)
    reason = _termination_reason(state, final_round, config.max_turns) or (
        "no_players_remaining"
    )
    return _result(config, state, final_round, reason, actions_log, events_log)


def _as_decision_agent(agent: SimulationAgent) -> DecisionAgent:
    from .agent_protocol import as_decision_agent

    if isinstance(agent, ObservationHeuristicAgent):
        return agent
    return as_decision_agent(agent)


def _validate_decision_agent_seats(
    state: GameState,
    decision_agents: Mapping[str, DecisionAgent],
) -> None:
    player_ids = set(state.players)
    agent_ids = set(decision_agents)
    if agent_ids != player_ids:
        missing = sorted(player_ids - agent_ids)
        extra = sorted(agent_ids - player_ids)
        raise ValueError(
            f"Decision agents must match players: missing={missing}, extra={extra}"
        )


def _create_state(config: SimulationConfig) -> GameState:
    return create_game_state(
        config.mode,
        player_count=config.players,
        seed=config.seed,
        press=config.press,
        variant_id=config.variant_id,
        # Table games run through the decision loop, which surfaces the opening
        # face-down commitment as SETUP_PLACE decisions. Postal keeps auto-commit.
        defer_opening_commitment=config.mode == "table",
    )


def _build_agent(agent_name: str, rng: SeededRNG) -> SimulationAgent:
    if agent_name == "random":
        return RandomAgent(rng)
    if agent_name == "heuristic":
        return HeuristicAgent(rng)
    if agent_name == "interactive":
        return InteractiveAgent(rng)
    if agent_name == DECISION_HEURISTIC_AGENT:
        return ObservationHeuristicAgent()
    raise ValueError(f"Unknown agent: {agent_name}")


def _legacy_agent(agent: SimulationAgent) -> LegacySimulationAgent:
    if isinstance(agent, ObservationHeuristicAgent):
        raise ValueError(f"Simulation agent {DECISION_HEURISTIC_AGENT} is table-only")
    return agent


def _termination_reason(state: GameState, turn: int, max_turns: int) -> str | None:
    if any(
        player.pending_orders.get("final_strike") for player in state.players.values()
    ):
        return "max_turns" if turn >= max_turns else None
    alive = [player for player in state.players.values() if player.alive]
    if len(alive) == 0:
        return "no_players_remaining"
    if len(alive) == 1:
        return "one_player_remaining"
    if turn >= max_turns:
        return "max_turns"
    return None


def _result(
    config: SimulationConfig,
    state: GameState,
    turns: int,
    reason: str,
    actions: list[dict[str, Any]],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    populations = final_populations(state)
    return {
        "mode": config.mode,
        "active_variant": resolve_requested_variant(
            state.variant_id,
            "Simulation",
        ).to_payload(),
        "seed": config.seed,
        "agent": config.agent,
        "players": config.players,
        "turns": turns,
        "winner": _winner(reason, populations),
        "termination_reason": reason,
        "final_populations": populations,
        "eliminations": [
            player_id for player_id, player in state.players.items() if not player.alive
        ],
        "pending_final_strikes": any(
            player.pending_orders.get("final_strike")
            for player in state.players.values()
        ),
        "actions": actions,
        "events": events,
    }


def _winner(termination_reason: str, populations: dict[str, int]) -> str | None:
    if termination_reason != "one_player_remaining":
        return None
    for player_id, population in populations.items():
        if population > 0:
            return player_id
    return None
