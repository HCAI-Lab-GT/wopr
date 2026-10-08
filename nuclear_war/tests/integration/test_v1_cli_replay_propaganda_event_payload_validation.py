"""CLI replay propaganda event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_postal_propaganda_ordered_event_boolean_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_propaganda_ordered_target.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["target"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    expected = "Replay event 0 postal_propaganda_ordered target must be a string"
    assert expected in captured.err


def test_cli_replay_rejects_propaganda_effect_event_boolean_migrated(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_propaganda_effect_migrated.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _propaganda_effect_event_payload()
    payload["events"][0]["payload"]["migrated"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    expected = "Replay event 0 propaganda_effect migrated must be an integer"
    assert expected in captured.err


def test_cli_replay_rejects_propaganda_effect_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_propaganda_effect_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _propaganda_effect_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 propaganda_effect payload fields are invalid" in captured.err


def _propaganda_effect_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "propaganda_effect",
        "player_id": "player_0",
        "card_id": "propaganda_1",
        "payload": {"target": "player_1", "migrated": 5},
    }


def _valid_replay_payload() -> dict:
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
        "final_populations": {"player_0": 35, "player_1": 25},
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
                "event_type": "postal_propaganda_ordered",
                "player_id": "player_0",
                "card_id": "propaganda_1",
                "payload": {"target": "player_1"},
            }
        ],
    }
