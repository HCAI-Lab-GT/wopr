"""CLI single-game replay players metadata validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_missing_players_metadata(tmp_path, capsys) -> None:
    invalid = tmp_path / "missing_players.json"
    payload = _valid_replay_payload()
    del payload["players"]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay file missing required field: players" in captured.err


def test_cli_replay_rejects_population_count_mismatch(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_population_count.json"
    payload = _valid_replay_payload()
    payload["final_populations"] = {"player_0": 30}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay final_populations count 1 does not match players: 2" in captured.err


def test_cli_replay_rejects_population_id_mismatch(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_population_ids.json"
    payload = _valid_replay_payload()
    payload["final_populations"] = {"player_0": 30, "rogue": 30}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay final_populations keys must match players" in captured.err


def test_cli_replay_rejects_unknown_winner(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_winner.json"
    payload = _valid_replay_payload()
    payload["winner"] = "rogue"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay winner must be a known player id or null" in captured.err


def test_cli_replay_rejects_winner_that_contradicts_populations(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_replay_winner_population.json"
    payload = _valid_replay_payload()
    payload["winner"] = "player_0"
    payload["termination_reason"] = "one_player_remaining"
    payload["eliminations"] = ["player_0"]
    payload["final_populations"] = {"player_0": 0, "player_1": 30}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay winner does not match final populations" in captured.err


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
