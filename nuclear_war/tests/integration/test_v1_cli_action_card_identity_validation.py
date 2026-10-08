"""CLI replay action card identity validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_enqueue_action_with_blank_card(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_enqueue_blank_card.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = 'player_0:enqueue:{"cards":["card_1",""]}'
    payload["actions"][0]["action_type"] = "enqueue"
    payload["actions"][0]["payload"] = {"cards": ["card_1", ""]}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 enqueue cards must identify cards" in captured.err


def test_cli_replay_rejects_target_action_with_blank_delivery(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_target_blank_delivery.json"
    payload = _valid_replay_payload()
    payload["actions"][0]["action_id"] = (
        'player_0:target:{"delivery":"","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "target"
    payload["actions"][0]["payload"] = {"delivery": "", "target": "player_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 target delivery must identify a card" in captured.err


def test_cli_replay_rejects_postal_card_target_action_with_blank_card(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_card_target_blank_card.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["actions"][0]["action_id"] = (
        'player_0:postal_propaganda:{"card":"","target":"player_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_propaganda"
    payload["actions"][0]["payload"] = {"card": "", "target": "player_1"}
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay action 0 postal_propaganda card must identify a card" in captured.err


def test_cli_replay_rejects_postal_equipment_action_with_blank_warhead(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_equipment_blank_warhead.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["actions"][0]["action_id"] = (
        'player_0:postal_cruise_launch:{"card":"card_1",'
        '"target":"player_1","warhead":""}'
    )
    payload["actions"][0]["action_type"] = "postal_cruise_launch"
    payload["actions"][0]["payload"] = {
        "card": "card_1",
        "target": "player_1",
        "warhead": "",
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_cruise_launch warhead must identify a card"
        in captured.err
    )


def test_cli_replay_rejects_postal_equipment_action_with_blank_card(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_postal_equipment_blank_card.json"
    payload = _valid_replay_payload()
    payload["mode"] = "postal"
    payload["actions"][0]["action_id"] = (
        'player_0:postal_cruise_launch:{"card":"",'
        '"target":"player_1","warhead":"warhead_1"}'
    )
    payload["actions"][0]["action_type"] = "postal_cruise_launch"
    payload["actions"][0]["payload"] = {
        "card": "",
        "target": "player_1",
        "warhead": "warhead_1",
    }
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay action 0 postal_cruise_launch card must identify a card" in captured.err
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
