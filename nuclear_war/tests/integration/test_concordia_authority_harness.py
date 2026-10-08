"""Concordia authority-seat harness integration tests."""

from __future__ import annotations

import pytest

from nuclear_war_concordia.agent import FirstLegalConcordiaClient
from nuclear_war_concordia.authority_config import (
    AuthorityConfig,
    AuthorityMemberConfig,
)
from nuclear_war_concordia.config import ConcordiaNoPressConfig, ConcordiaSeatConfig
from nuclear_war_concordia.harness import run_concordia_no_press_game
from nuclear_war_concordia.press_config import PressConfig


def test_full_press_authority_uses_configured_spokesperson(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clients: list[TrackingFirstLegalClient] = []

    class TrackingFirstLegalClient(FirstLegalConcordiaClient):
        def __init__(self) -> None:
            self.press_calls = 0
            clients.append(self)

        def complete(self, scene_text: str) -> str:
            if '"decision_type": "press"' in scene_text:
                self.press_calls += 1
            return super().complete(scene_text)

    monkeypatch.setattr(
        "nuclear_war_concordia.harness_agents.FirstLegalConcordiaClient",
        TrackingFirstLegalClient,
    )
    result = run_concordia_no_press_game(_authority_config())

    message = next(
        item
        for item in result["press_artifact"]["messages"]
        if item["speaker"] == "player_0"
    )
    assert message["rendered_observation"]["identity"]["name"] == "Executive"
    assert result["replay"]["turns"] == 2
    assert clients[0].press_calls > 0
    assert clients[1].press_calls == 0
    assert clients[2].press_calls == 0


def _authority_config() -> ConcordiaNoPressConfig:
    seats = {
        "player_0": ConcordiaSeatConfig(
            agent="concordia_first_legal",
            identity={"name": "Faction Zero", "role": "strategic actor"},
            authority=AuthorityConfig(
                archetype="sole_authority",
                parameters={"deference": 0.0},
                spokesperson="executive",
                members=(
                    _member("executive", "Executive"),
                    _member("strategic_advisor", "Strategic Advisor"),
                    _member("risk_advisor", "Risk Advisor"),
                ),
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
    return ConcordiaNoPressConfig(
        players=4,
        seed=81,
        max_turns=2,
        seats=seats,
        press=PressConfig(mode="full_press", enabled=True, passes=1),
    )


def _member(member_id: str, name: str) -> AuthorityMemberConfig:
    return AuthorityMemberConfig(
        member_id=member_id,
        identity={"name": name, "role": "authority member"},
    )
