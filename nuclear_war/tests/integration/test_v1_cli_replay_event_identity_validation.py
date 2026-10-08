"""CLI replay event identity validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_card_scoped_event_with_null_card_id(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_event_null_card_id.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "card_drawn",
        "player_id": "player_0",
        "card_id": None,
        "payload": {},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 card_drawn card_id must identify a card" in captured.err


def test_cli_replay_rejects_card_scoped_event_with_blank_card_id(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_event_blank_card_id.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "card_drawn",
        "player_id": "player_0",
        "card_id": "",
        "payload": {},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 card_drawn card_id must identify a card" in captured.err


def test_cli_replay_rejects_postal_card_scoped_event_with_null_card_id(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_event_null_card_id.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["events"][0] = {
        "turn": 1,
        "event_type": "postal_atomic_cannon_fire_ordered",
        "player_id": "player_0",
        "card_id": None,
        "payload": {},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    expected = (
        "Replay event 0 postal_atomic_cannon_fire_ordered card_id "
        "must identify a cannon"
    )
    assert expected in captured.err


def test_cli_replay_rejects_runtime_event_with_null_player_id(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_runtime_event_null_player_id.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "launch_declared",
        "player_id": None,
        "card_id": "delivery_1",
        "payload": {"target": "player_1", "warheads": ["warhead_1"], "yield": 10},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 launch_declared player_id must identify a player"
        in captured.err
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
