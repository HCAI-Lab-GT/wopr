"""CLI replay event mode validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_phase_complete_in_table_replay(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_table_phase_complete_event.json"
    payload = _valid_replay_payload()
    payload["events"][0]["event_type"] = "phase_complete"
    payload["events"][0]["payload"] = {"phase": "launch"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 event_type requires postal mode" in captured.err


def test_cli_replay_rejects_phase_complete_with_unknown_phase(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_phase_complete_phase.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["events"][0]["event_type"] = "phase_complete"
    payload["events"][0]["player_id"] = None
    payload["events"][0]["payload"] = {"phase": "made_up"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 phase_complete phase has invalid value" in captured.err


def test_cli_replay_rejects_player_scoped_phase_complete(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_phase_complete_player.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["events"][0]["event_type"] = "phase_complete"
    payload["events"][0]["player_id"] = "player_0"
    payload["events"][0]["payload"] = {"phase": "launch"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 phase_complete player_id must be null" in captured.err


def test_cli_replay_rejects_phase_complete_extra_payload_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_phase_complete_payload.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["events"][0]["event_type"] = "phase_complete"
    payload["events"][0]["player_id"] = None
    payload["events"][0]["payload"] = {"phase": "launch", "extra": "ignored"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 phase_complete payload fields are invalid" in captured.err


def test_cli_replay_rejects_supervirus_event_in_table_replay(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_table_supervirus_event.json"
    payload = _valid_replay_payload()
    payload["events"][0]["event_type"] = "supervirus_wiped_out"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 event_type requires postal mode" in captured.err


def test_cli_replay_rejects_cruise_event_in_table_replay(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_table_cruise_event.json"
    payload = _valid_replay_payload()
    payload["events"][0]["event_type"] = "cruise_launched"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay event 0 event_type requires postal mode" in captured.err


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
