"""CLI replay queue event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_cards_enqueued_event_string_cards(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_cards_enqueued_event_cards.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _cards_enqueued_event_payload()
    payload["events"][0]["payload"]["cards"] = "card_1"
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 cards_enqueued cards must be a list" in captured.err


def test_cli_replay_rejects_cards_enqueued_event_blank_card(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_cards_enqueued_event_blank_card.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _cards_enqueued_event_payload()
    payload["events"][0]["payload"]["cards"] = ["card_1", ""]
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 cards_enqueued cards must identify cards" in captured.err


def test_cli_replay_rejects_queue_updated_event_string_cards(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_queue_updated_event_cards.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _queue_updated_event_payload()
    payload["events"][0]["payload"]["cards"] = "card_1"
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 queue_updated cards must be a list" in captured.err


def _cards_enqueued_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "cards_enqueued",
        "player_id": "player_0",
        "card_id": None,
        "payload": {"cards": ["card_1"]},
    }


def _queue_updated_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "queue_updated",
        "player_id": "player_0",
        "card_id": None,
        "payload": {"cards": ["card_1"]},
    }


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
