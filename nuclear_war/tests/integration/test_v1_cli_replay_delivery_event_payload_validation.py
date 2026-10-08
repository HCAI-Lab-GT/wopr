"""CLI replay delivery event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_delivery_ready_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_delivery_ready_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 delivery_ready payload fields are invalid" in captured.err


def test_cli_replay_rejects_delivery_ready_event_boolean_capacity(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_delivery_ready_capacity.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["capacity"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 delivery_ready capacity must be an integer" in captured.err


def test_cli_replay_rejects_delivery_ready_event_boolean_previous(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_delivery_ready_previous.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["previous"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 delivery_ready previous must be a string or null"
        in captured.err
    )


def test_cli_replay_rejects_delivery_ready_event_blank_previous(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_delivery_ready_blank_previous.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["previous"] = ""
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 delivery_ready previous must identify a card" in captured.err


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
                "event_type": "delivery_ready",
                "player_id": "player_0",
                "card_id": "delivery_1",
                "payload": {"capacity": 2, "previous": None},
            }
        ],
    }
