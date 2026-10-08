"""Press scene rendering tests."""

from __future__ import annotations

from nuclear_war_concordia.press_scene import render_press_scene


def test_render_press_scene_includes_speaker_observation_and_prior_messages() -> None:
    observation = _observation(player_id="player_0")
    prior_messages = [
        {"turn": 1, "speaker": "player_1", "text": "Stand down.", "audience": "public"}
    ]

    scene = render_press_scene(
        observation=observation,
        identity={"name": "Commander 0"},
        prior_messages=prior_messages,
        validation_feedback=["Previous message was empty"],
    )

    payload = scene.payload
    assert payload["player_id"] == "player_0"
    assert payload["identity"] == {"name": "Commander 0"}
    assert payload["prior_messages"] == prior_messages
    assert payload["decision_type"] == "press"
    options = payload["legal_options"]
    assert [option["action_id"] for option in options] == ["decline", "speak"]
    assert "speak" in scene.text
    assert "decline" in scene.text


def test_render_press_scene_accepts_empty_prior_messages() -> None:
    scene = render_press_scene(
        observation=_observation(player_id="player_2"),
        identity={"name": "Commander 2"},
        prior_messages=[],
        validation_feedback=[],
    )

    assert scene.payload["prior_messages"] == []


def test_render_press_scene_uses_full_press_options_when_provided() -> None:
    from nuclear_war_concordia.press_scene import full_press_options

    scene = render_press_scene(
        observation=_observation(player_id="player_0"),
        identity={"name": "Commander 0"},
        prior_messages=[],
        validation_feedback=[],
        options=full_press_options(),
    )

    options = scene.payload["legal_options"]
    assert [option["action_id"] for option in options] == [
        "decline",
        "speak",
        "whisper",
    ]
    assert "whisper" in scene.text
    assert "commitment" in scene.text


def test_render_press_scene_full_press_describes_private_channel() -> None:
    from nuclear_war_concordia.press_scene import full_press_options

    scene = render_press_scene(
        observation=_observation(player_id="player_0"),
        identity={"name": "Commander 0"},
        prior_messages=[],
        validation_feedback=[],
        options=full_press_options(),
    )

    assert "whisper privately" in scene.text
    assert "commitment" in scene.text


def _observation(player_id: str):
    from nuclear_war_env.observation import observe
    from nuclear_war_env.setup_game import create_game_state

    state = create_game_state("table", player_count=4, seed=81)
    return observe(state, player_id)
