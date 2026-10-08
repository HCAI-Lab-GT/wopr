"""CLI single-game replay metadata validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_invalid_replay_mode(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_mode.json"
    payload = _valid_replay_payload()
    payload["mode"] = "space"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay has invalid mode: space" in captured.err


def test_cli_replay_rejects_invalid_replay_agent(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_agent.json"
    payload = _valid_replay_payload()
    payload["agent"] = "scripted"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay has invalid agent: scripted" in captured.err


def test_cli_replay_rejects_replay_without_variant_object(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_variant.json"
    payload = _valid_replay_payload()
    payload["active_variant"] = "base_later_two_d10"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay active_variant must be an object" in captured.err


def test_cli_replay_rejects_replay_without_population_object(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_populations.json"
    payload = _valid_replay_payload()
    payload["final_populations"] = [["player_0", 30]]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay final_populations must be an object" in captured.err


def test_cli_replay_rejects_replay_without_integer_seed(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_seed.json"
    payload = _valid_replay_payload()
    payload["seed"] = "3"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay seed must be an integer" in captured.err


def test_cli_replay_rejects_replay_without_string_winner(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_winner.json"
    payload = _valid_replay_payload()
    payload["winner"] = 7
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay winner must be a string or null" in captured.err


def test_cli_replay_rejects_replay_without_string_termination(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_termination.json"
    payload = _valid_replay_payload()
    payload["termination_reason"] = None
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay termination_reason must be a string" in captured.err


def test_cli_replay_rejects_replay_without_integer_population(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_population_value.json"
    payload = _valid_replay_payload()
    payload["final_populations"]["player_0"] = "30"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay final_populations player_0 must be an integer" in captured.err


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
