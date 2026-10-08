"""CLI replay log player-id validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_action_with_unknown_player_id(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_player_id.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["player_id"] = "rogue"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 player_id must be a known player id" in captured.err


def test_cli_replay_rejects_event_with_unknown_player_id(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_event_player_id.json"
    payload = _valid_replay_payload()
    payload["events"][0]["player_id"] = "rogue"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 player_id must be a known player id or null" in captured.err


def test_cli_replay_rejects_player_scoped_event_with_null_player_id(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_event_null_player_id.json"
    payload = _valid_replay_payload()
    payload["events"][0]["player_id"] = None
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 action_passed player_id must identify a player" in captured.err
    )


def test_cli_replay_rejects_action_id_with_wrong_player(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_id_player.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = "player_1:pass"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 action_id player must match player_id" in captured.err


def test_cli_replay_rejects_action_id_with_wrong_type(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_id_type.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = "player_0:draw"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 action_id type must match action_type" in captured.err


def test_cli_replay_rejects_action_id_with_wrong_payload_suffix(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_action_id_payload.json"
    payload = _valid_replay_payload()
    payload["actions"][0] = {
        "turn": 1,
        "player_id": "player_0",
        "action_id": "player_0:target:delivery:player_0",
        "action_type": "target",
        "payload": {"delivery": "delivery", "target": "player_1"},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 action_id payload must match payload" in captured.err


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
