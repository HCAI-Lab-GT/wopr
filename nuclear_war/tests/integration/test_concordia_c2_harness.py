"""Composed authority and press-condition integration tests."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import pytest

from nuclear_war_concordia.artifacts import write_concordia_no_press_artifacts
from nuclear_war_concordia.config import load_concordia_no_press_config
from nuclear_war_concordia.harness import run_concordia_no_press_game


@pytest.mark.parametrize("archetype", ["sole_authority", "council"])
def test_c2_press_matrix_preserves_replay_and_complete_deliberations(
    archetype: str,
    authority_config_payload: dict[str, object],
) -> None:
    no_press = _run_condition(authority_config_payload, archetype, press=False)
    full_press = _run_condition(authority_config_payload, archetype, press=True)

    assert _replay_bytes(full_press) == _replay_bytes(no_press)
    for result in (no_press, full_press):
        deliberations = result["c2_artifact"]["deliberations"]
        assert deliberations
        assert result["c2_artifact"]["authority_players"] == ["player_0"]
        assert all(len(item["members"]) == 3 for item in deliberations)
        assert result["summary"]["channel_metrics"]["c2"]["trace_count"] == (
            len(deliberations) * 3
        )
        assert result["summary"]["channel_metrics"]["c2"]["call_count"] == (
            len(deliberations) * 3
        )
    assert no_press["summary"]["channel_metrics"]["press"]["call_count"] == 0
    assert full_press["summary"]["channel_metrics"]["press"]["call_count"] > 0


def test_authority_run_writes_nonempty_c2_sidecar(
    authority_config_payload: dict[str, object],
    tmp_path: Path,
) -> None:
    result = _run_condition(
        authority_config_payload,
        "sole_authority",
        press=False,
    )

    paths = write_concordia_no_press_artifacts(tmp_path, result)
    written = json.loads(paths["c2_path"].read_text(encoding="utf-8"))

    assert written == result["c2_artifact"]
    assert written["deliberations"]


@pytest.mark.parametrize(
    ("filename", "archetype"),
    [
        ("concordia_c2_sole_authority_offline.json", "sole_authority"),
        ("concordia_c2_council_offline.json", "council"),
    ],
)
def test_offline_authority_example_loads(
    filename: str,
    archetype: str,
) -> None:
    path = Path("docs/examples") / filename
    payload = json.loads(path.read_text(encoding="utf-8"))

    config = load_concordia_no_press_config(payload)

    assert config.press.mode == "full_press"
    assert config.seats["player_0"].authority is not None
    assert config.seats["player_0"].authority.archetype == archetype


def _run_condition(
    base_payload: dict[str, object],
    archetype: str,
    *,
    press: bool,
) -> dict[str, Any]:
    payload = deepcopy(base_payload)
    payload["max_turns"] = 2
    seats = cast(dict[str, dict[str, Any]], payload["seats"])
    authority = cast(dict[str, Any], seats["player_0"]["authority"])
    authority["archetype"] = archetype
    if archetype == "council":
        authority["parameters"] = {
            "threshold": 0.5,
            "weights": {
                "executive": 1.0,
                "strategic_advisor": 1.0,
                "risk_advisor": 1.0,
            },
        }
    if press:
        payload["press"] = {
            "mode": "full_press",
            "enabled": True,
            "passes": 1,
        }
    config = load_concordia_no_press_config(payload)
    return run_concordia_no_press_game(config)


def _replay_bytes(result: dict[str, Any]) -> bytes:
    return json.dumps(result["replay"], sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
