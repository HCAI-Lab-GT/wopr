"""CLI replay action payload validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_enqueue_action_with_non_list_cards(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_enqueue_payload.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = 'player_0:enqueue:{"cards":"card_1"}'
    payload["actions"][0]["action_type"] = "enqueue"
    payload["actions"][0]["payload"] = {"cards": "card_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 enqueue cards must be a list" in captured.err


def test_cli_replay_rejects_postal_vote_peace_action_with_payload(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_vote_peace_payload.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["actions"][0]["action_id"] = 'player_0:postal_vote_peace:{"ignored":true}'
    payload["actions"][0]["action_type"] = "postal_vote_peace"
    payload["actions"][0]["payload"] = {"ignored": True}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 postal_vote_peace payload must be empty" in captured.err


def test_cli_replay_rejects_postal_propaganda_action_missing_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_propaganda_payload.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["actions"][0]["action_id"] = 'player_0:postal_propaganda:{"card":"card_1"}'
    payload["actions"][0]["action_type"] = "postal_propaganda"
    payload["actions"][0]["payload"] = {"card": "card_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_propaganda payload fields are invalid" in captured.err
    )


def test_cli_replay_rejects_postal_secret_target_action_missing_target(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_secret_target_payload.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["actions"][0]["action_id"] = (
        'player_0:postal_secret_target:{"secret":"card_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_secret_target"
    payload["actions"][0]["payload"] = {"secret": "card_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_secret_target payload fields are invalid"
        in captured.err
    )


def test_cli_replay_rejects_postal_steal_secret_action_extra_field(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_steal_secret_payload.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["actions"][0]["action_id"] = (
        'player_0:postal_steal_secret:{"ignored":true,"target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_steal_secret"
    payload["actions"][0]["payload"] = {"target": "player_1", "ignored": True}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_steal_secret payload fields are invalid" in captured.err
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
