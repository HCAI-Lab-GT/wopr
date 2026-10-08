"""Command-authority condition artifact tests."""

from __future__ import annotations

import json

from nuclear_war_agents import HTTPClientConfig
from nuclear_war_concordia.authority_config import (
    AuthorityConfig,
    AuthorityMemberConfig,
)
from nuclear_war_concordia.config import ConcordiaNoPressConfig, ConcordiaSeatConfig
from nuclear_war_concordia.harness_payloads import agent_metadata, config_snapshot
from nuclear_war_concordia.press_config import PressConfig


def test_condition_artifacts_record_press_and_authority_without_secret(
    monkeypatch,
) -> None:
    monkeypatch.setenv("WOPR_TEST_API_KEY", "resolved-secret")
    config = _config()

    snapshot = config_snapshot(config)
    metadata = agent_metadata(config)

    assert snapshot["press"] == {
        "mode": "full_press",
        "enabled": True,
        "passes": 2,
    }
    assert snapshot["seats"]["player_0"]["authority"] == _authority_payload()
    assert metadata["player_0"]["authority"] == _authority_payload()
    assert metadata["player_0"]["press"] == snapshot["press"]
    dumped = json.dumps({"snapshot": snapshot, "metadata": metadata})
    assert "WOPR_TEST_API_KEY" in dumped
    assert "resolved-secret" not in dumped


def _config() -> ConcordiaNoPressConfig:
    identity = {"name": "Commander", "role": "strategic actor"}
    authority_seat = ConcordiaSeatConfig(
        agent="concordia_http",
        identity=identity,
        client=HTTPClientConfig(
            base_url="http://localhost:8000/v1",
            model="test-model",
            api_key_env="WOPR_TEST_API_KEY",
        ),
        authority=_authority(),
    )
    plain_seat = ConcordiaSeatConfig(
        agent="concordia_first_legal",
        identity=identity,
    )
    return ConcordiaNoPressConfig(
        players=4,
        seed=7,
        seats={
            "player_0": authority_seat,
            "player_1": plain_seat,
            "player_2": plain_seat,
            "player_3": plain_seat,
        },
        press=PressConfig(mode="full_press", enabled=True, passes=2),
    )


def _authority() -> AuthorityConfig:
    return AuthorityConfig(
        archetype="sole_authority",
        parameters={"deference": 0.0},
        spokesperson="executive",
        members=tuple(
            AuthorityMemberConfig(
                member_id=member_id,
                identity={"name": name, "role": role},
            )
            for member_id, name, role in (
                ("executive", "Executive", "final authority"),
                ("strategic_advisor", "Strategic Advisor", "strategy"),
                ("risk_advisor", "Risk Advisor", "risk"),
            )
        ),
    )


def _authority_payload() -> dict[str, object]:
    return {
        "archetype": "sole_authority",
        "parameters": {"deference": 0.0},
        "spokesperson": "executive",
        "members": [
            {
                "member_id": member.member_id,
                "identity": dict(member.identity),
            }
            for member in _authority().members
        ],
    }
