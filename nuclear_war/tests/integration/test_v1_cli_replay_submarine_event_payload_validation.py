"""CLI replay submarine event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_submarine_strike_event_boolean_loss(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_submarine_strike_loss.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["loss"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 submarine_strike loss must be an integer" in captured.err


def test_cli_replay_rejects_submarine_returned_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_submarine_returned_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _submarine_returned_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 submarine_returned payload fields are invalid" in captured.err
    )


def test_cli_replay_rejects_postal_submarine_launch_event_boolean_yield(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_submarine_launch_yield.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _postal_submarine_launch_event_payload()
    payload["events"][0]["payload"]["warhead_yield"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 postal_submarine_launch_ordered warhead_yield "
        "must be an integer"
    ) in captured.err


def _submarine_returned_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "submarine_returned",
        "player_id": "player_0",
        "card_id": "submarine_1",
        "payload": {},
    }


def _postal_submarine_launch_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "postal_submarine_launch_ordered",
        "player_id": "player_0",
        "card_id": "submarine_1",
        "payload": {"target": "player_1", "warhead_yield": 20},
    }


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
        "final_populations": {"player_0": 30, "player_1": 10},
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
                "event_type": "submarine_strike",
                "player_id": "player_0",
                "card_id": "submarine_1",
                "payload": {"target": "player_1", "loss": 20, "yield": 20},
            }
        ],
    }
