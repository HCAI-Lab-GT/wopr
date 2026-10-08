"""CLI replay press-event validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_press_event(tmp_path, capsys) -> None:
    invalid = tmp_path / "press_event.json"
    payload = _valid_replay_payload()
    payload["events"][0]["event_type"] = "press_entry"
    payload["events"][0]["payload"] = {"message": "hello"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Postal press is deferred until after v1" in captured.err


def test_cli_replay_rejects_press_enabled_flag(tmp_path, capsys) -> None:
    invalid = tmp_path / "press_enabled.json"
    payload = _valid_replay_payload()
    payload["press"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Postal press is deferred until after v1" in captured.err


def test_cli_replay_rejects_malformed_press_flag(tmp_path, capsys) -> None:
    invalid = tmp_path / "press_malformed.json"
    payload = _valid_replay_payload()
    payload["press"] = 0
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Press must be false for v1" in captured.err


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
