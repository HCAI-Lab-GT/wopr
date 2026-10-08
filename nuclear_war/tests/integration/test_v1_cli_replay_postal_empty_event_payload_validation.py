"""CLI replay postal empty event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_postal_peace_voted_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_peace_voted_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "postal_peace_voted",
        "player_id": "player_0",
        "card_id": None,
        "payload": {"extra": True},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 postal_peace_voted payload fields are invalid" in captured.err
    )


def test_cli_replay_rejects_postal_defense_ordered_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_defense_ordered_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "postal_defense_ordered",
        "player_id": "player_0",
        "card_id": "antimissile_1",
        "payload": {"extra": True},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 postal_defense_ordered payload fields are invalid"
        in captured.err
    )


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
