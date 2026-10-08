"""CLI replay eliminated-event identity validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_player_eliminated_event_without_player_id(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_eliminated_event_player_id.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "player_eliminated",
        "player_id": None,
        "card_id": None,
        "payload": {"by": "player_0"},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 player_eliminated player_id must be the eliminated player"
        in captured.err
    )


def test_cli_replay_rejects_player_eliminated_event_by_self(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_eliminated_event_by_self.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "player_eliminated",
        "player_id": "player_1",
        "card_id": None,
        "payload": {"by": "player_1"},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 player_eliminated by must not be the eliminated player"
        in captured.err
    )


def test_cli_replay_rejects_player_eliminated_event_missing_from_summary(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_eliminated_event_summary.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "player_eliminated",
        "player_id": "player_1",
        "card_id": None,
        "payload": {"by": "player_0"},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 player_eliminated player_id must be listed in eliminations"
        in captured.err
    )


def test_cli_replay_rejects_duplicate_player_eliminated_event(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_duplicate_eliminated_event.json"
    payload = _valid_replay_payload()
    payload["winner"] = "player_0"
    payload["termination_reason"] = "one_player_remaining"
    payload["eliminations"] = ["player_1"]
    payload["final_populations"]["player_1"] = 0
    event = {
        "turn": 1,
        "event_type": "player_eliminated",
        "player_id": "player_1",
        "card_id": None,
        "payload": {"by": "player_0"},
    }
    payload["events"] = [event, dict(event)]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 1 player_eliminated player_id must not duplicate an earlier "
        "elimination event"
    ) in captured.err


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
