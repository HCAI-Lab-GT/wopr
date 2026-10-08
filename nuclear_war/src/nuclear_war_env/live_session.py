from dataclasses import dataclass, field
from typing import Any

from nuclear_war_agents import ObservationHeuristicAgent

from . import decision_loop as loop
from . import live_session_payloads as p
from .action_models import LegalAction
from .engine.decision import Decision
from .observation import observe
from .setup_game import create_game_state as create_state
from .simulation import _termination_reason
from .state import GameState
from .variants import ACTIVE_VARIANT_ID


@dataclass(frozen=True)
class LiveSessionConfig:
    players: int = 3
    seed: int = 42
    max_turns: int = 50
    controlled_players: tuple[str, ...] = ("player_0",)
    variant_id: str = ACTIVE_VARIANT_ID


class LiveSessionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass
class LiveSession:
    config: LiveSessionConfig
    state: GameState
    state_version: int
    _actions_log: list[dict[str, Any]] = field(default_factory=list)
    _events_log: list[dict[str, Any]] = field(default_factory=list)
    _recent_events: list[dict[str, Any]] = field(default_factory=list)
    _termination: str | None = None

    @classmethod
    def start(cls, config: LiveSessionConfig) -> "LiveSession":
        cfg = config
        state = create_state(
            "table",
            cfg.players,
            cfg.seed,
            False,
            cfg.variant_id,
            defer_opening_commitment=True,
        )
        unknown = sorted(set(cfg.controlled_players) - set(state.players))
        if unknown:
            raise LiveSessionError("unknown_player", f"Unknown players: {unknown}")
        session = cls(config=cfg, state=state, state_version=1)
        session._record(loop.start_game(state, stop_at_round_boundary=True))
        session._resume_if_needed()
        session._sync_terminal_completion()
        return session

    def session_payload(self) -> dict[str, Any]:
        return p.session_payload(
            self.state,
            self.config.seed,
            self.config.controlled_players,
            self.state_version,
            self._termination is not None,
        )

    def state_payload(self) -> dict[str, Any]:
        return p.state_payload(
            self.state,
            state_version=self.state_version,
            source_label="live local session",
            recent_events=self._recent_events,
        )

    def decision_payload(self) -> dict[str, Any]:
        return p.decision_payload(loop.pending_decision(self.state), self.state_version)

    def apply_action_id(self, action_id: str, state_version: int) -> dict[str, Any]:
        self._require_current_version(state_version)
        decision = self._require_pending_decision()
        if decision.agent_id not in self.config.controlled_players:
            raise LiveSessionError("agent_player", "Agent player decision.")
        action = next((a for a in decision.options if a.action_id == action_id), None)
        if action is None:
            raise LiveSessionError("unknown_action", "Action id is not legal.")
        return self._mutation_payload(self._apply_action(action))

    def step_agent(self, state_version: int) -> dict[str, Any]:
        self._require_current_version(state_version)
        decision = self._require_pending_decision()
        if decision.agent_id in self.config.controlled_players:
            raise LiveSessionError("controlled_player", "Controlled player decision.")
        obs = observe(self.state, decision.agent_id)
        action = ObservationHeuristicAgent().choose(obs, decision.options)
        return self._mutation_payload(self._apply_action(action))

    def artifacts_payload(self) -> dict[str, Any]:
        return p.artifacts_payload(
            self.state,
            self.config.seed,
            self.config.players,
            self._termination,
            self._actions_log,
            self._events_log,
        )

    def _require_current_version(self, state_version: int) -> None:
        if state_version != self.state_version:
            raise LiveSessionError("stale_state", "State version changed.")

    def _require_pending_decision(self) -> Decision:
        decision = loop.pending_decision(self.state)
        if decision is None:
            raise LiveSessionError("no_pending_decision", "No decision is pending.")
        return decision

    def _apply_action(self, action: LegalAction) -> list[dict[str, Any]]:
        events = self._record(loop.apply_decision_result(self.state, action, True))
        events.extend(self._resume_if_needed())
        self._sync_terminal_completion()
        self.state_version += 1
        return events

    def _mutation_payload(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "ok": True,
            "state_version": self.state_version,
            "events": events,
            "decision": self.decision_payload(),
        }

    def _resume_if_needed(self) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        while loop.at_round_boundary(self.state):
            turn = p.current_turn(self.state)
            reason = _termination_reason(self.state, turn, self.config.max_turns)
            if reason is not None:
                self._termination = reason
                return events
            events.extend(self._record(loop.resume_round(self.state, True)))
        return events

    def _sync_terminal_completion(self) -> None:
        pending = loop.pending_decision(self.state)
        if self._termination is not None or pending is not None:
            return
        if not loop.at_round_boundary(self.state):
            turn = max(1, (self.state.cursor.round - 1) if self.state.cursor else 1)
            reason = _termination_reason(self.state, turn, self.config.max_turns)
            self._termination = reason or "no_players_remaining"

    def _record(self, batch: loop._RoundStamper) -> list[dict[str, Any]]:
        events = p.record_batch(self._actions_log, self._events_log, batch)
        self._recent_events = events[-20:] if events else self._recent_events
        return events
