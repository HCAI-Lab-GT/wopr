"""CLI replay postal equipment target identity validation tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_env.action_models import payload_suffix
from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


@pytest.mark.parametrize(
    ("action_type", "payload", "field", "label"),
    [
        (
            "postal_space_platform_drop",
            {"platform": "", "target": "player_1"},
            "platform",
            "platform",
        ),
        (
            "postal_submarine_reload",
            {"submarine": "", "target": "player_1", "warhead": "warhead_1"},
            "submarine",
            "submarine",
        ),
        (
            "postal_submarine_reload",
            {"submarine": "submarine_1", "target": "player_1", "warhead": ""},
            "warhead",
            "card",
        ),
        ("postal_submarine_fire", {"submarine": ""}, "submarine", "submarine"),
        ("postal_submarine_return", {"submarine": ""}, "submarine", "submarine"),
    ],
)
def test_cli_replay_rejects_postal_equipment_target_blank_identifier(
    tmp_path, capsys, action_type: str, payload: dict, field: str, label: str
) -> None:
    invalid = tmp_path / f"bad_{action_type}_{field}.json"
    replay = _valid_postal_replay_payload()
    replay["actions"][0] = {
        "turn": 1,
        "player_id": "player_0",
        "action_id": f"player_0:{action_type}{payload_suffix(payload)}",
        "action_type": action_type,
        "payload": payload,
    }
    invalid.write_text(json.dumps(replay), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        f"Replay action 0 {action_type} {field} must identify a {label}" in captured.err
    )


def _valid_postal_replay_payload() -> dict:
    return {
        "mode": "postal",
        "active_variant": ACTIVE_VARIANT.to_payload(),
        "seed": 3,
        "agent": "heuristic",
        "players": 2,
        "winner": None,
        "turns": 1,
        "termination_reason": "max_turns",
        "eliminations": [],
        "final_populations": {"player_0": 30, "player_1": 30},
        "actions": [
            {
                "turn": 1,
                "player_id": "player_0",
                "action_id": "player_0:pass",
                "action_type": "pass",
                "payload": {},
            }
        ],
        "events": [
            {
                "turn": 1,
                "event_type": "action_passed",
                "player_id": "player_0",
                "card_id": None,
                "payload": {},
            }
        ],
    }
