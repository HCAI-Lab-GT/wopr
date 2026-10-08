"""CLI replay previous-only card event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_defense_prepared_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_defense_prepared_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "defense_prepared",
        "player_id": "player_0",
        "card_id": "antimissile_1",
        "payload": {"previous": "delivery_1", "extra": True},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 defense_prepared payload fields are invalid" in captured.err


def test_cli_replay_rejects_card_resolved_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_card_resolved_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "card_resolved",
        "player_id": "player_0",
        "card_id": "special_1",
        "payload": {"previous": "delivery_1", "extra": True},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 card_resolved payload fields are invalid" in captured.err


def test_cli_replay_rejects_defense_prepared_event_blank_previous(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_defense_prepared_blank_previous.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "defense_prepared",
        "player_id": "player_0",
        "card_id": "antimissile_1",
        "payload": {"previous": ""},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 defense_prepared previous must identify a card" in captured.err
    )


def _valid_replay_payload() -> dict:
    return {
        "mode": "table",
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
