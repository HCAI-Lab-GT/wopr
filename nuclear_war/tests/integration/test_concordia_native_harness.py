"""Native Concordia harness integration tests."""

from __future__ import annotations

import importlib
import os

import pytest

# Every test in this module needs gdm-concordia. The guard imports the real
# package (not find_spec) so broken installs are caught, and runs before the
# project imports so a future top-level concordia import in the project
# cannot crash collection first. Set WOPR_REQUIRE_CONCORDIA to any non-empty
# value to turn an unavailable install into a failure instead of a skip.
try:
    importlib.import_module("concordia")
except ImportError as exc:
    if os.environ.get("WOPR_REQUIRE_CONCORDIA"):
        pytest.fail(
            f"WOPR_REQUIRE_CONCORDIA is set but gdm-concordia is unavailable: {exc}",
            pytrace=False,
        )
    pytest.skip("requires gdm-concordia", allow_module_level=True)

from nuclear_war_concordia.config import (  # noqa: E402
    ConcordiaNoPressConfig,
    ConcordiaSeatConfig,
)
from nuclear_war_concordia.harness import run_concordia_no_press_game  # noqa: E402
from nuclear_war_env.llm_trace_artifacts import validate_trace_artifact  # noqa: E402
from nuclear_war_env.replay_validation import validate_replay_payload  # noqa: E402


def test_native_first_legal_four_agent_game_uses_runtime() -> None:
    result = run_concordia_no_press_game(_native_config())

    validate_replay_payload(result["replay"])
    validate_trace_artifact(result["trace_artifact"], result["replay"])
    assert result["runtime"]["runtime_path"] == "concordia_runtime"
    assert result["summary"]["runtime_path"] == "concordia_runtime"
    assert result["summary"]["trace_count"] >= 1


def test_native_game_prompts_contain_scene_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import types

    from nuclear_war_concordia import native

    prompts: list[str] = []
    no_language_model = importlib.import_module(
        "concordia.language_model.no_language_model"
    )

    class SpyModel(no_language_model.NoLanguageModel):
        def sample_choice(self, prompt, responses, *, seed=None):
            del seed
            prompts.append(prompt)
            return 0, responses[0], {}

    monkeypatch.setattr(
        native,
        "_no_language_model_module",
        lambda: types.SimpleNamespace(NoLanguageModel=SpyModel),
    )

    result = run_concordia_no_press_game(_native_config())

    assert result["summary"]["runtime_path"] == "concordia_runtime"
    assert prompts, "no prompt reached the native model"
    for prompt in prompts:
        assert "Scene JSON:" in prompt
        assert '"population"' in prompt
        assert '"legal_options"' in prompt


def test_native_game_traces_record_entity_log() -> None:
    result = run_concordia_no_press_game(_native_config())

    traces = result["trace_artifact"]["traces"]
    assert traces
    for trace in traces:
        entity_log = trace["rendered_observation"]["concordia"]["entity_log"]
        act_prompt = "\n".join(entity_log["__act__"]["Prompt"])
        assert "Scene JSON:" in act_prompt
    validate_trace_artifact(result["trace_artifact"], result["replay"])


def test_native_first_legal_same_seed_games_are_identical() -> None:
    first = run_concordia_no_press_game(_native_config())
    second = run_concordia_no_press_game(_native_config())

    assert first["replay"] == second["replay"]
    assert first["trace_artifact"] == second["trace_artifact"]
    assert first["summary"] == second["summary"]


def test_concordia_runtime_rejects_non_native_seats() -> None:
    seats = {
        f"player_{index}": ConcordiaSeatConfig(
            agent="concordia_first_legal",
            identity={"name": f"Commander {index}"},
        )
        for index in range(4)
    }

    with pytest.raises(ValueError, match="requires native Concordia seats"):
        run_concordia_no_press_game(
            _native_config(runtime="concordia_runtime", seats=seats)
        )


def _native_config(
    runtime: str = "auto",
    seats: dict[str, ConcordiaSeatConfig] | None = None,
) -> ConcordiaNoPressConfig:
    return ConcordiaNoPressConfig(
        players=4,
        seed=67,
        max_turns=1,
        runtime=runtime,
        seats=seats or _native_seats(),
    )


def _native_seats() -> dict[str, ConcordiaSeatConfig]:
    return {
        f"player_{index}": ConcordiaSeatConfig(
            agent="concordia_native_first_legal",
            identity={"name": f"Commander {index}"},
        )
        for index in range(4)
    }
