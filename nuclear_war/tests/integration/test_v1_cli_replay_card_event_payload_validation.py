"""CLI replay card event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_warhead_loaded_event_numeric_delivery(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_warhead_loaded_delivery.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["delivery"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 warhead_loaded delivery must be a string" in captured.err


def test_cli_replay_rejects_warhead_loaded_event_boolean_previous(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_warhead_loaded_previous.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["previous"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 warhead_loaded previous must be a string or null"
        in captured.err
    )


def test_cli_replay_rejects_warhead_discarded_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_warhead_discarded_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _warhead_discarded_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 warhead_discarded payload fields are invalid" in captured.err


def test_cli_replay_rejects_warhead_discarded_event_numeric_reason(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_warhead_discarded_reason.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _warhead_discarded_event_payload()
    payload["events"][0]["payload"]["reason"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 warhead_discarded reason must be a string" in captured.err


def test_cli_replay_rejects_warhead_discarded_event_boolean_previous(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_warhead_discarded_previous.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _warhead_discarded_event_payload()
    payload["events"][0]["payload"]["previous"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 warhead_discarded previous must be a string or null"
        in captured.err
    )


def test_cli_replay_rejects_propaganda_ready_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_propaganda_ready_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _propaganda_ready_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 propaganda_ready payload fields are invalid" in captured.err


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


def _warhead_discarded_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "warhead_discarded",
        "player_id": "player_0",
        "card_id": "warhead_1",
        "payload": {"reason": "no_delivery", "previous": "delivery_1"},
    }


def _propaganda_ready_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "propaganda_ready",
        "player_id": "player_0",
        "card_id": "propaganda_1",
        "payload": {"previous": "delivery_1"},
    }
