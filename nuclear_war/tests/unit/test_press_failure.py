"""Press failure path tests."""

from __future__ import annotations

from nuclear_war_concordia.failure import ConcordiaDecisionFailure, press_failure
from nuclear_war_concordia.types import ConcordiaScene, ParsedPressMessage


def test_press_failure_returns_decision_failure_with_press_fields() -> None:
    scene = ConcordiaScene(text="scene", payload={"player_id": "player_0", "turn": 2})

    failure = press_failure(
        "No valid press message",
        speaker="player_0",
        round_no=2,
        audience="public",
        pass_no=1,
        prior_messages=[],
        scene=scene,
        prompts=["prompt"],
        raw_responses=["garbage"],
        completions=[],
        validation_errors=["empty message"],
        parsed=ParsedPressMessage(),
    )

    assert isinstance(failure, ConcordiaDecisionFailure)
    snapshot = failure.snapshot
    assert snapshot["speaker"] == "player_0"
    assert snapshot["round"] == 2
    assert snapshot["audience"] == "public"
    assert snapshot["pass"] == 1
    assert snapshot["decision_type"] == "press"
    assert snapshot["validation_errors"] == ["empty message"]
