"""Concordia no-press harness recovery from transient client faults.

Spec failure model: one recoverable provider fault (timeout/HTTP error) is
retried once so a live game is not aborted by a single network blip; a
persistent fault fails the run. Determinism must survive the retry path.
"""

from __future__ import annotations

import json

import pytest

from nuclear_war_agents import LLMHttpError
from nuclear_war_concordia.agent import FirstLegalConcordiaClient
from nuclear_war_concordia.config import ConcordiaNoPressConfig, ConcordiaSeatConfig
from nuclear_war_concordia.failure import ConcordiaRunFailure
from nuclear_war_concordia.harness import run_concordia_no_press_game
from nuclear_war_env.llm_trace_artifacts import validate_trace_artifact
from nuclear_war_env.replay_validation import validate_replay_payload

_FLAKY_TARGET = "nuclear_war_concordia.harness_agents.FirstLegalConcordiaClient"


def test_game_completes_despite_single_transient_fault(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(_FLAKY_TARGET, _FailOnceFirstLegalClient)

    result = run_concordia_no_press_game(_first_legal_config())

    validate_replay_payload(result["replay"])
    validate_trace_artifact(result["trace_artifact"], result["replay"])
    assert result["summary"]["fallback_count"] == 0
    # A transient provider blip is a transport retry, not a bad model action.
    assert result["summary"]["invalid_action_count"] == 0
    assert result["summary"]["recoverable_provider_retry_count"] >= 1
    assert _has_recorded_transient_retry(result["trace_artifact"]["traces"])


def test_persistent_transient_fault_fails_the_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(_FLAKY_TARGET, _AlwaysFailingClient)

    with pytest.raises(ConcordiaRunFailure):
        run_concordia_no_press_game(_first_legal_config())


def test_transient_recovery_is_byte_identical_across_runs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(_FLAKY_TARGET, _FailOnceFirstLegalClient)

    first = run_concordia_no_press_game(_first_legal_config())
    second = run_concordia_no_press_game(_first_legal_config())

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_non_flaky_run_is_byte_identical_across_runs() -> None:
    first = run_concordia_no_press_game(_first_legal_config())
    second = run_concordia_no_press_game(_first_legal_config())

    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


class _FailOnceFirstLegalClient:
    """Raise one recoverable fault per instance, then choose first legal."""

    def __init__(self) -> None:
        self._inner = FirstLegalConcordiaClient()
        self._failed = False

    def complete(self, scene_text: str) -> str:
        if not self._failed:
            self._failed = True
            raise LLMHttpError("transient provider blip")
        return self._inner.complete(scene_text)


class _AlwaysFailingClient:
    def __init__(self) -> None:
        pass

    def complete(self, scene_text: str) -> str:
        del scene_text
        raise LLMHttpError("provider down")


def _has_recorded_transient_retry(traces: list[dict]) -> bool:
    return any(trace["recoverable_provider_retries"] >= 1 for trace in traces)


def _first_legal_config(max_turns: int = 3) -> ConcordiaNoPressConfig:
    seats = {
        f"player_{index}": ConcordiaSeatConfig(
            agent="concordia_first_legal",
            identity={"name": f"Commander {index}", "role": "strategic actor"},
        )
        for index in range(4)
    }
    return ConcordiaNoPressConfig(players=4, seed=61, max_turns=max_turns, seats=seats)
