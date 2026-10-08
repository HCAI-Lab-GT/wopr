"""CLI replay atomic cannon event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_atomic_cannon_fired_event_boolean_loss(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_atomic_cannon_fired_loss.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["loss"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 atomic_cannon_fired loss must be an integer" in captured.err


def test_cli_replay_rejects_atomic_cannon_repositioned_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_atomic_cannon_repositioned_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _atomic_cannon_repositioned_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 atomic_cannon_repositioned payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_atomic_cannon_failed_event_boolean_reason(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_atomic_cannon_failed_reason.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _atomic_cannon_failed_event_payload()
    payload["events"][0]["payload"]["reason"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 atomic_cannon_failed reason must be a string" in captured.err


def test_cli_replay_rejects_atomic_cannon_setup_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_atomic_cannon_setup_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _atomic_cannon_setup_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 atomic_cannon_setup payload fields are invalid" in captured.err
    )


def _atomic_cannon_repositioned_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "atomic_cannon_repositioned",
        "player_id": "player_0",
        "card_id": "atomic_cannon_1",
        "payload": {"target": "player_1"},
    }


def _atomic_cannon_failed_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "atomic_cannon_failed",
        "player_id": "player_0",
        "card_id": "atomic_cannon_1",
        "payload": {"reason": "not_ready"},
    }


def _atomic_cannon_setup_event_payload() -> dict:
    return {
        "turn": 1,
        "event_type": "atomic_cannon_setup",
        "player_id": "player_0",
        "card_id": "atomic_cannon_1",
        "payload": {},
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
        "final_populations": {"player_0": 30, "player_1": 20},
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
                "event_type": "atomic_cannon_fired",
                "player_id": "player_0",
                "card_id": "atomic_cannon_1",
                "payload": {"target": "player_1", "loss": 10, "yield": 10},
            }
        ],
    }
