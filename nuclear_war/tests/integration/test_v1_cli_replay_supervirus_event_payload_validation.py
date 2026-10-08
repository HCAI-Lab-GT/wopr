"""CLI replay supervirus event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_supervirus_started_event_boolean_loss(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_supervirus_started_loss.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["loss"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 supervirus_started loss must be an integer" in captured.err


def test_cli_replay_rejects_supervirus_retained_event_boolean_turns_held(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_supervirus_retained_turns_held.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _supervirus_retained_event_payload()
    payload["events"][0]["payload"]["turns_held"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 supervirus_retained turns_held must be an integer"
        in captured.err
    )


def test_cli_replay_rejects_supervirus_wiped_out_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_supervirus_wiped_out_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _supervirus_wiped_out_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    expected = "Replay event 0 supervirus_wiped_out payload fields are invalid"
    assert expected in captured.err


def test_cli_replay_rejects_postal_supervirus_pass_event_boolean_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_supervirus_pass_target.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _postal_supervirus_pass_event_payload()
    payload["events"][0]["payload"]["target"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 postal_supervirus_pass_ordered target must be a string"
        in captured.err
    )


def _supervirus_retained_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "supervirus_retained",
        "player_id": "player_1",
        "card_id": "supervirus_1",
        "payload": {"turns_held": 2},
    }


def _supervirus_wiped_out_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "supervirus_wiped_out",
        "player_id": "player_1",
        "card_id": "supervirus_1",
        "payload": {},
    }


def _postal_supervirus_pass_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "postal_supervirus_pass_ordered",
        "player_id": "player_1",
        "card_id": None,
        "payload": {"target": "player_0"},
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
        "final_populations": {"player_0": 25, "player_1": 30},
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
                "event_type": "supervirus_started",
                "player_id": "player_0",
                "card_id": "supervirus_1",
                "payload": {"target": "player_1", "loss": 5},
            }
        ],
    }
