from __future__ import annotations

import pytest

from nuclear_war_concordia.config import (
    ConcordiaNoPressConfig,
    ConcordiaSeatConfig,
)
from nuclear_war_concordia.harness import run_concordia_no_press_game
from nuclear_war_concordia.types import ConcordiaRuntimeStatus
from nuclear_war_env.llm_trace_artifacts import validate_trace_artifact
from nuclear_war_env.replay_validation import validate_replay_payload


def test_concordia_no_press_game_runs_four_first_legal_agents() -> None:
    result = run_concordia_no_press_game(_first_legal_config(max_turns=3))

    validate_replay_payload(result["replay"])
    validate_trace_artifact(result["trace_artifact"], result["replay"])
    # Per-seat Concordia agents are honestly labelled "mixed_seats" in the replay.
    assert result["replay"]["agent"] == "mixed_seats"
    assert result["runtime"]["runtime_path"] == "concordia_style_fallback"
    assert result["summary"]["trace_count"] >= 1
    assert result["summary"]["fallback_count"] == 0
    assert set(result["agent_metadata"]) == set(_first_legal_seats())


def test_replay_agent_is_driver_label_while_metadata_names_true_agents() -> None:
    # The replay "agent" is the honest per-seat driver label "mixed_seats", not
    # any one seat's policy. Honesty is preserved because agent_metadata reports
    # each seat's true agent. This guards against the label being mistaken for
    # the actual decision policy.
    result = run_concordia_no_press_game(_first_legal_config(max_turns=3))

    assert result["replay"]["agent"] == "mixed_seats"
    assert all(
        meta["agent"] == "concordia_first_legal"
        for meta in result["agent_metadata"].values()
    )


def test_concordia_no_press_game_fails_on_invalid_scripted_agent() -> None:
    seats = _first_legal_seats()
    seats["player_0"] = ConcordiaSeatConfig(
        agent="concordia_scripted",
        identity={"name": "Broken Commander"},
        scripted_responses=("not-json", "still-not-json"),
    )

    with pytest.raises(ValueError, match="No legal Concordia action selected"):
        run_concordia_no_press_game(_config(seats))


def test_concordia_no_press_game_requires_real_runtime_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_runtime(
        monkeypatch,
        ConcordiaRuntimeStatus(
            runtime_path="concordia_style_fallback",
            available=False,
            detail="missing concordia",
        ),
    )

    with pytest.raises(ValueError, match="requires native Concordia seats"):
        run_concordia_no_press_game(_first_legal_config(runtime="concordia_runtime"))


def test_concordia_no_press_game_records_execution_runtime_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_runtime(
        monkeypatch,
        ConcordiaRuntimeStatus(
            runtime_path="concordia_runtime",
            available=True,
            detail="imported concordia",
            version="test",
        ),
    )

    result = run_concordia_no_press_game(_first_legal_config())

    assert result["runtime"]["runtime_path"] == "concordia_style_fallback"
    assert result["runtime"]["detected_runtime_path"] == "concordia_runtime"
    assert result["summary"]["runtime_path"] == "concordia_style_fallback"


def test_concordia_config_defaults_press_to_none() -> None:
    from nuclear_war_concordia.press_config import PressConfig

    config = ConcordiaNoPressConfig(
        players=4,
        seed=61,
        seats=_first_legal_seats(),
    )
    assert config.press == PressConfig(mode="none", enabled=False)


def _patch_runtime(mp: pytest.MonkeyPatch, status: ConcordiaRuntimeStatus) -> None:
    mp.setattr(
        "nuclear_war_concordia.harness.detect_concordia_runtime",
        lambda: status,
    )


def _first_legal_config(
    max_turns: int = 1,
    runtime: str = "auto",
) -> ConcordiaNoPressConfig:
    return _config(_first_legal_seats(), max_turns=max_turns, runtime=runtime)


def _config(
    seats: dict[str, ConcordiaSeatConfig],
    max_turns: int = 1,
    runtime: str = "auto",
) -> ConcordiaNoPressConfig:
    return ConcordiaNoPressConfig(
        players=4, seed=61, max_turns=max_turns, runtime=runtime, seats=seats
    )


def _first_legal_seats() -> dict[str, ConcordiaSeatConfig]:
    return {
        f"player_{index}": ConcordiaSeatConfig(
            agent="concordia_first_legal",
            identity={"name": f"Commander {index}", "role": "strategic actor"},
        )
        for index in range(4)
    }
