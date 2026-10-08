"""Partial C2 state preservation on authority-member failure."""

from __future__ import annotations

import json
from typing import Any, cast

import pytest

from nuclear_war_concordia.agent import FirstLegalConcordiaClient
from nuclear_war_concordia.config import load_concordia_no_press_config
from nuclear_war_concordia.failure import ConcordiaRunFailure
from nuclear_war_concordia.harness import run_concordia_no_press_game


def test_authority_failure_snapshot_retains_partial_member_state(
    authority_config_payload: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    credential_marker = "c2-credential-marker"

    class FailThirdMemberAfterOneDeliberationClient:
        created = 0

        def __init__(self, _config: object) -> None:
            self.index = self.created
            self.calls = 0
            type(self).created += 1

        def complete(self, scene_text: str) -> str:
            self.calls += 1
            if self.index == 2 and self.calls >= 2:
                return "not-json"
            response = json.loads(FirstLegalConcordiaClient().complete(scene_text))
            response["rationale"] = credential_marker
            return json.dumps(response)

    monkeypatch.setattr(
        "nuclear_war_concordia.harness_agents.LLMHttpClient",
        FailThirdMemberAfterOneDeliberationClient,
    )
    monkeypatch.setenv("WOPR_C2_TEST_KEY", credential_marker)
    seats = cast(dict[str, dict[str, Any]], authority_config_payload["seats"])
    seats["player_0"]["agent"] = "concordia_http"
    seats["player_0"]["client"] = {
        "base_url": "https://example.invalid/v1",
        "model": "test-model",
        "api_key_env": "WOPR_C2_TEST_KEY",
    }
    authority_config_payload["max_turns"] = 2
    config = load_concordia_no_press_config(authority_config_payload)

    with pytest.raises(ConcordiaRunFailure) as raised:
        run_concordia_no_press_game(config)

    partial = raised.value.snapshot["decision_failure"]["c2_partial_state"]
    seat = partial["seats"]["player_0"]
    assert partial["authority_players"] == ["player_0"]
    assert len(seat["completed_deliberations"]) == 1
    assert len(seat["completed_deliberations"][0]["member_votes"]) == 3
    assert len(seat["member_traces"]["executive"]) == 2
    assert len(seat["member_traces"]["strategic_advisor"]) == 2
    assert len(seat["member_traces"]["risk_advisor"]) == 1
    snapshot_text = json.dumps(raised.value.snapshot)
    assert credential_marker not in snapshot_text
    assert "[redacted]" in snapshot_text
