"""CLI replay secret event payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_postal_secret_targeted_event_boolean_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_secret_targeted_target.json"
    payload = _valid_replay_payload()
    payload["events"][0]["payload"]["target"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    expected = "Replay event 0 postal_secret_targeted target must be a string"
    assert expected in captured.err


def test_cli_replay_rejects_secret_stolen_event_boolean_from(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_secret_stolen_from.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _secret_stolen_event_payload()
    payload["events"][0]["payload"]["from"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 secret_stolen from must be a string" in captured.err


def test_cli_replay_rejects_secret_population_stolen_event_boolean_migrated(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_secret_population_stolen_migrated.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _secret_population_stolen_event_payload()
    payload["events"][0]["payload"]["migrated"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    expected = "Replay event 0 secret_population_stolen migrated must be an integer"
    assert expected in captured.err


def test_cli_replay_rejects_secret_population_damaged_event_boolean_loss(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_secret_population_damaged_loss.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _secret_population_damaged_event_payload()
    payload["events"][0]["payload"]["loss"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    expected = "Replay event 0 secret_population_damaged loss must be an integer"
    assert expected in captured.err


def test_cli_replay_rejects_secret_population_gained_event_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_secret_population_gained_payload.json"
    payload = _valid_replay_payload()
    payload["events"][0] = _secret_population_gained_event_payload()
    payload["events"][0]["payload"]["extra"] = True
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    code = main(["replay", str(invalid)])
    captured = capsys.readouterr()
    assert code == 2
    expected = "Replay event 0 secret_population_gained payload fields are invalid"
    assert expected in captured.err


def _secret_stolen_event_payload() -> dict:
    return _event("secret_stolen", {"from": "player_1"})


def _secret_population_stolen_event_payload() -> dict:
    return _event("secret_population_stolen", {"target": "player_1", "migrated": 5})


def _secret_population_damaged_event_payload() -> dict:
    return _event("secret_population_damaged", {"loss": 5})


def _secret_population_gained_event_payload() -> dict:
    return _event("secret_population_gained", {})


def _event(event_type: str, payload: dict) -> dict:
    return {
        "turn": 1,
        "event_type": event_type,
        "player_id": "player_0",
        "card_id": "secret_1",
        "payload": payload,
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
        "final_populations": {"player_0": 30, "player_1": 25},
        "actions": [
            {
                "turn": 1,
                "player_id": "player_0",
                "action_id": "player_0:pass",
                "action_type": "pass",
                "payload": {},
            }
        ],
        "events": [_event("postal_secret_targeted", {"target": "player_1"})],
    }
