"""CLI replay card event identity validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_warhead_loaded_event_blank_delivery(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_warhead_loaded_blank_delivery.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["delivery"] = ""
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 warhead_loaded delivery must identify a card" in captured.err


def test_cli_replay_rejects_warhead_loaded_event_blank_previous(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_warhead_loaded_blank_previous.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["previous"] = ""
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 warhead_loaded previous must identify a card" in captured.err


def test_cli_replay_rejects_warhead_discarded_event_blank_previous(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_warhead_discarded_blank_previous.json"
    payload = _valid_replay_payload()
    payload["events"][0] = {
        "turn": 1,
        "event_type": "warhead_discarded",
        "player_id": "player_0",
        "card_id": "warhead_1",
        "payload": {"reason": "no_delivery", "previous": ""},
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 warhead_discarded previous must identify a card" in captured.err
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
                "event_type": "warhead_loaded",
                "player_id": "player_0",
                "card_id": "warhead_1",
                "payload": {"delivery": "delivery_1", "previous": "delivery_1"},
            }
        ],
    }
