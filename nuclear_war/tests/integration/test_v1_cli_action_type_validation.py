"""CLI replay action type validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_unknown_action_type(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_action_type_value.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_type"] = "launch_everything"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 action_type has invalid value: launch_everything"
        in captured.err
    )


def test_cli_replay_rejects_postal_action_in_table_replay(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_table_postal_action.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = "player_0:postal_propaganda"
    payload["actions"][0]["action_type"] = "postal_propaganda"
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 action_type requires postal mode" in captured.err


def test_cli_replay_rejects_pass_action_with_payload(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_pass_payload.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = 'player_0:pass:{"ignored":true}'
    payload["actions"][0]["payload"] = {"ignored": True}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 pass payload must be empty" in captured.err


def test_cli_replay_rejects_draw_action_with_payload(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_draw_payload.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = 'player_0:draw:{"ignored":true}'
    payload["actions"][0]["action_type"] = "draw"
    payload["actions"][0]["payload"] = {"ignored": True}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 draw payload must be empty" in captured.err


def test_cli_replay_rejects_target_action_missing_target(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_target_payload.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = 'player_0:target:{"delivery":"card_1"}'
    payload["actions"][0]["action_type"] = "target"
    payload["actions"][0]["payload"] = {"delivery": "card_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 target payload fields are invalid" in captured.err


def test_cli_replay_rejects_final_strike_action_missing_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_final_strike_payload.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = 'player_0:final_strike_target:{"ignored":true}'
    payload["actions"][0]["action_type"] = "final_strike_target"
    payload["actions"][0]["payload"] = {"ignored": True}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 final_strike_target payload fields are invalid" in captured.err
    )


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
