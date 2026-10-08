"""CLI replay event payload player-reference validation tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


@pytest.mark.parametrize(
    ("event_type", "payload", "field"),
    [
        ("target_declared", {"target": "rogue"}, "target"),
        ("warhead_detonated", {"target": "rogue", "yield": 20, "loss": 20}, "target"),
        ("player_eliminated", {"by": "rogue"}, "by"),
        (
            "equipment_destroyed",
            {"target_player": "rogue", "kind": "atomic_cannon", "equipment": "a"},
            "target_player",
        ),
    ],
)
def test_cli_replay_rejects_event_payload_unknown_player_reference(
    tmp_path, capsys, event_type: str, payload: dict, field: str
) -> None:
    invalid = tmp_path / f"bad_{event_type}_{field}.json"
    replay = _valid_replay_payload()
    replay["events"][0] = {
        "turn": 1,
        "event_type": event_type,
        "player_id": "player_0",
        "card_id": _card_id_for_event(event_type),
        "payload": payload,
    }
    invalid.write_text(json.dumps(replay), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        f"Replay event 0 {event_type} {field} must be a known player id" in captured.err
    )


def test_cli_replay_rejects_event_payload_self_target(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_event_payload_self_target.json"
    replay = _valid_replay_payload()
    replay["events"][0] = {
        "turn": 1,
        "event_type": "target_declared",
        "player_id": "player_0",
        "card_id": "delivery_1",
        "payload": {"target": "player_0"},
    }
    invalid.write_text(json.dumps(replay), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay event 0 target_declared target must not be the acting player"
        in captured.err
    )


def _card_id_for_event(event_type: str) -> str | None:
    if event_type in {"equipment_destroyed", "target_declared"}:
        return "delivery_1"
    return None


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
