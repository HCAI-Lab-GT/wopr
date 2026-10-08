"""Press-light harness integration tests."""

from __future__ import annotations

import pytest

from nuclear_war_agents import HTTPClientConfig
from nuclear_war_concordia.config import (
    ConcordiaNoPressConfig,
    ConcordiaSeatConfig,
)
from nuclear_war_concordia.harness import run_concordia_no_press_game
from nuclear_war_concordia.press_artifacts import validate_press_artifact
from nuclear_war_env.replay_validation import validate_replay_payload


def test_press_light_run_writes_press_traces_and_unchanged_replay() -> None:
    result = run_concordia_no_press_game(_first_legal_press_config(max_turns=2))

    validate_replay_payload(result["replay"])
    validate_press_artifact(result["press_artifact"], result["replay"])
    messages = result["press_artifact"]["messages"]
    assert len(messages) >= 4
    assert all(message["audience"] == "public" for message in messages)
    assert all(message["visibility"] == "public" for message in messages)
    assert all(message["pass"] == 1 for message in messages)
    assert all(message["parse_result"]["declined"] for message in messages)


def test_press_enabled_reproduces_no_press_replay() -> None:
    """Enabling press must not perturb the WOPR replay at the same seed."""
    no_press = run_concordia_no_press_game(
        _first_legal_config(max_turns=2, press_mode="none")
    )
    press = run_concordia_no_press_game(_first_legal_press_config(max_turns=2))

    assert press["replay"] == no_press["replay"]
    assert "press_artifact" not in no_press
    assert "press_artifact" in press
    assert press["press_artifact"]["messages"]


def test_press_light_run_writes_sidecar_and_summary(tmp_path) -> None:
    import json as _json

    from nuclear_war_concordia.artifacts import write_concordia_no_press_artifacts

    result = run_concordia_no_press_game(_first_legal_press_config(max_turns=2))

    paths = write_concordia_no_press_artifacts(tmp_path, result)

    assert paths["press_path"].exists()
    payload = _json.loads(paths["press_path"].read_text())
    assert payload["press_mode"] == "press_light"
    assert result["summary"]["press_message_count"] == len(
        result["press_artifact"]["messages"]
    )


def test_press_light_style_demo_config_loads() -> None:
    import json

    from nuclear_war_concordia.config import load_concordia_no_press_config

    payload = json.load(open("docs/examples/concordia_press_light_style_demo.json"))
    config = load_concordia_no_press_config(payload)

    assert config.press.mode == "press_light"
    assert config.press.enabled is True


def test_press_light_fails_hard_on_broken_press_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class BrokenPressClient:
        def __init__(self, config: HTTPClientConfig) -> None:
            del config

        def complete(self, scene_text: str) -> str:
            if "public press message" in scene_text:
                return "not json"
            return _first_legal_response(scene_text)

    def _first_legal_response(scene_text: str) -> str:
        from nuclear_war_concordia.agent import FirstLegalConcordiaClient

        return FirstLegalConcordiaClient().complete(scene_text)

    monkeypatch.setattr(
        "nuclear_war_concordia.harness_agents.LLMHttpClient", BrokenPressClient
    )
    seats = {
        f"player_{index}": ConcordiaSeatConfig(
            agent="concordia_http",
            identity={"name": f"Commander {index}", "role": "strategic actor"},
            client=HTTPClientConfig(
                base_url="http://localhost:8000/v1",
                model="demo-model",
                api_key_env="TOGETHER_API_KEY",
            ),
        )
        for index in range(4)
    }
    with pytest.raises(ValueError, match="press message"):
        run_concordia_no_press_game(_config(seats, max_turns=2))


@pytest.mark.parametrize(
    "native_agent",
    ["concordia_native_first_legal", "concordia_native_http"],
)
def test_press_rejects_native_seats(native_agent: str) -> None:
    from nuclear_war_concordia.press_config import PressConfig

    seats = {
        f"player_{index}": ConcordiaSeatConfig(
            agent=native_agent,
            identity={"name": f"Commander {index}", "role": "strategic actor"},
            client=HTTPClientConfig(
                base_url="http://localhost:8000/v1",
                model="demo-model",
                api_key_env="TOGETHER_API_KEY",
            ),
        )
        for index in range(4)
    }
    config = ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=2,
        seats=seats,
        press=PressConfig(mode="press_light", enabled=True),
    )
    with pytest.raises(ValueError, match="native"):
        run_concordia_no_press_game(config)


def test_reject_native_press_seats_helper_contract() -> None:
    """The gate helper flags native seats and passes non-native ones.

    Scoping to the press-enabled branch is covered by
    test_press_rejects_native_seats (native seat + press enabled raises); the
    native seat + press-disabled end-to-end path is covered in
    tests/integration/test_concordia_native_harness.py.
    """
    from nuclear_war_concordia.harness import _reject_native_press_seats

    native = ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=2,
        seats={
            "player_0": ConcordiaSeatConfig(
                agent="concordia_native_first_legal",
                identity={"name": "Commander 0"},
            )
        },
    )
    with pytest.raises(ValueError, match="native"):
        _reject_native_press_seats(native)

    non_native = ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=2,
        seats={
            "player_0": ConcordiaSeatConfig(
                agent="concordia_first_legal",
                identity={"name": "Commander 0"},
            )
        },
    )
    _reject_native_press_seats(non_native)  # must not raise for non-native seats


def _first_legal_press_config(max_turns: int) -> ConcordiaNoPressConfig:
    return _config(_first_legal_press_seats(), max_turns=max_turns)


def _first_legal_config(
    max_turns: int, press_mode: str = "none"
) -> ConcordiaNoPressConfig:
    from nuclear_war_concordia.press_config import PressConfig

    return ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=max_turns,
        seats=_first_legal_press_seats(),
        press=PressConfig(mode=press_mode, enabled=(press_mode != "none")),
    )


def _first_legal_press_seats() -> dict[str, ConcordiaSeatConfig]:
    return {
        f"player_{index}": ConcordiaSeatConfig(
            agent="concordia_first_legal",
            identity={"name": f"Commander {index}", "role": "strategic actor"},
        )
        for index in range(4)
    }


def _config(seats, max_turns: int) -> ConcordiaNoPressConfig:
    from nuclear_war_concordia.press_config import PressConfig

    return ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=max_turns,
        seats=seats,
        press=PressConfig(mode="press_light", enabled=True),
    )


def test_multi_turn_public_run_writes_multi_pass_traces() -> None:
    from nuclear_war_concordia.press_config import PressConfig

    config = ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=2,
        seats=_first_legal_press_seats(),
        press=PressConfig(mode="multi_turn_public", enabled=True, passes=2),
    )
    result = run_concordia_no_press_game(config)

    validate_replay_payload(result["replay"])
    validate_press_artifact(result["press_artifact"], result["replay"])
    messages = result["press_artifact"]["messages"]
    assert len(messages) >= 8
    assert all(message["audience"] == "public" for message in messages)
    passes = {message["pass"] for message in messages}
    assert passes == {1, 2}


def test_multi_turn_public_fails_hard_on_broken_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nuclear_war_concordia.press_config import PressConfig

    class BrokenPressClient:
        def __init__(self, config: HTTPClientConfig) -> None:
            del config

        def complete(self, scene_text: str) -> str:
            if "public press message" in scene_text:
                return "not json"
            from nuclear_war_concordia.agent import FirstLegalConcordiaClient

            return FirstLegalConcordiaClient().complete(scene_text)

    monkeypatch.setattr(
        "nuclear_war_concordia.harness_agents.LLMHttpClient", BrokenPressClient
    )
    seats = {
        f"player_{index}": ConcordiaSeatConfig(
            agent="concordia_http",
            identity={"name": f"Commander {index}", "role": "strategic actor"},
            client=HTTPClientConfig(
                base_url="http://localhost:8000/v1",
                model="demo-model",
                api_key_env="TOGETHER_API_KEY",
            ),
        )
        for index in range(4)
    }
    config = ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=2,
        seats=seats,
        press=PressConfig(mode="multi_turn_public", enabled=True, passes=2),
    )
    with pytest.raises(ValueError, match="press message"):
        run_concordia_no_press_game(config)


def test_multi_turn_public_demo_config_loads() -> None:
    import json

    from nuclear_war_concordia.config import load_concordia_no_press_config

    payload = json.load(
        open("docs/examples/concordia_multi_turn_public_style_demo.json")
    )
    config = load_concordia_no_press_config(payload)

    assert config.press.mode == "multi_turn_public"
    assert config.press.enabled is True
    assert config.press.passes == 2


def test_full_press_run_writes_full_press_traces_and_unchanged_replay() -> None:
    from nuclear_war_concordia.press_config import PressConfig

    config = ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=2,
        seats=_first_legal_press_seats(),
        press=PressConfig(mode="full_press", enabled=True, passes=2),
    )
    result = run_concordia_no_press_game(config)

    validate_replay_payload(result["replay"])
    validate_press_artifact(result["press_artifact"], result["replay"])
    messages = result["press_artifact"]["messages"]
    assert len(messages) >= 8
    assert result["press_artifact"]["press_mode"] == "full_press"
    passes = {message["pass"] for message in messages}
    assert passes == {1, 2}


def test_full_press_first_legal_produces_only_declines(tmp_path) -> None:
    from nuclear_war_concordia.press_config import PressConfig

    config = ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=2,
        seats=_first_legal_press_seats(),
        press=PressConfig(mode="full_press", enabled=True, passes=1),
    )
    result = run_concordia_no_press_game(config)

    messages = result["press_artifact"]["messages"]
    assert all(message["parse_result"]["declined"] for message in messages)
    assert all(message["visibility"] == "public" for message in messages)


def test_full_press_demo_config_loads() -> None:
    import json

    from nuclear_war_concordia.config import load_concordia_no_press_config

    payload = json.load(open("docs/examples/concordia_full_press_style_demo.json"))
    config = load_concordia_no_press_config(payload)

    assert config.press.mode == "full_press"
    assert config.press.enabled is True
    assert config.press.passes == 2


def test_full_press_reproduces_no_press_replay_byte_identical() -> None:
    from nuclear_war_concordia.press_config import PressConfig

    no_press = run_concordia_no_press_game(_first_legal_config(max_turns=2))
    full_press = run_concordia_no_press_game(
        ConcordiaNoPressConfig(
            players=4,
            seed=81,
            max_turns=2,
            seats=_first_legal_press_seats(),
            press=PressConfig(mode="full_press", enabled=True, passes=2),
        )
    )

    assert no_press["replay"] == full_press["replay"]


def test_full_press_decision_memory_excludes_private_from_nonparticipants(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from nuclear_war_concordia.agent import FirstLegalConcordiaClient
    from nuclear_war_concordia.press_config import PressConfig

    class WhisperingClient:
        def __init__(self, recipient: str, message: str) -> None:
            self._recipient = recipient
            self._message = message
            self._first_legal = FirstLegalConcordiaClient()

        def complete(self, scene_text: str):
            if "whisper privately" in scene_text:
                return (
                    '{"action_id": "whisper", "to": "'
                    f"{self._recipient}"
                    f'", "message": "{self._message}"}}'
                )
            return self._first_legal.complete(scene_text)

    whisper_text = "Secret alliance proposal."
    seats = {
        "player_0": ConcordiaSeatConfig(
            agent="concordia_http",
            identity={"name": "Commander 0", "role": "strategic actor"},
            client=HTTPClientConfig(
                base_url="http://localhost:8000/v1",
                model="demo-model",
                api_key_env="WOPR_TEST_API_KEY",
            ),
        ),
        **{
            f"player_{index}": ConcordiaSeatConfig(
                agent="concordia_first_legal",
                identity={"name": f"Commander {index}", "role": "strategic actor"},
            )
            for index in range(1, 4)
        },
    }
    monkeypatch_target = "nuclear_war_concordia.harness_agents.LLMHttpClient"

    monkeypatch.setattr(
        monkeypatch_target,
        lambda _config: WhisperingClient("player_1", whisper_text),
    )
    config = ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=3,
        seats=seats,
        press=PressConfig(mode="full_press", enabled=True, passes=1),
    )
    result = run_concordia_no_press_game(config)

    private_msg = next(
        m
        for m in result["press_artifact"]["messages"]
        if m.get("visibility") == "private"
    )
    assert private_msg["speaker"] == "player_0"
    assert private_msg["recipient"] == "player_1"

    for trace in result["trace_artifact"]["traces"]:
        scene = trace["rendered_observation"]["concordia"]["scene"]
        press_memory = scene.get("press_memory", [])
        viewer = trace["player_id"]
        for msg in press_memory:
            if msg.get("visibility") == "private":
                assert viewer in {
                    msg.get("speaker"),
                    msg.get("recipient"),
                }, f"non-participant {viewer} saw private message in decision scene"
