"""CLI replay active variant validation tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.variants import ACTIVE_VARIANT


def test_cli_replay_rejects_replay_variant_missing_randomizer(tmp_path, capsys) -> None:
    invalid = tmp_path / "bad_replay_variant_field.json"
    payload = _valid_replay_payload()
    del payload["active_variant"]["randomizer"]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay active_variant missing required field: randomizer" in captured.err


def test_cli_replay_rejects_experiment_variant_missing_randomizer(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_experiment_variant_field.json"
    payload = _valid_experiment_payload()
    del payload["results"][0]["active_variant"]["randomizer"]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Experiment result 0 active_variant missing required field: randomizer"
        in captured.err
    )


def test_cli_replay_rejects_replay_variant_missing_trading_enabled(
    tmp_path, capsys
) -> None:
    invalid = tmp_path / "bad_replay_variant_schema_field.json"
    payload = _valid_replay_payload()
    payload["active_variant"] = _full_variant_payload()
    del payload["active_variant"]["trading_enabled"]
    invalid.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["replay", str(invalid)])

    captured = capsys.readouterr()
    assert code == 2
    assert (
        "Replay active_variant missing required field: trading_enabled" in captured.err
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


def _full_variant_payload() -> dict[str, object]:
    return {
        "variant_id": "base_later_two_d10",
        "hand_draw_target": 10,
        "population_deck_size": 40,
        "randomizer": "base_two_d10_fallout_chart",
        "initial_face_down_cards": 2,
        "anti_missile_turn_jump": True,
        "expansion_sets": [],
        "special_powers_enabled": False,
        "trading_enabled": False,
        "press_enabled": False,
        "simultaneous_orders": False,
    }


def _valid_experiment_payload() -> dict:
    return {
        "mode": "table",
        "players": 2,
        "seed_start": 5,
        "runs": 1,
        "agent": "random",
        "max_turns": 50,
        "press": False,
        "results": [
            {
                "seed": 5,
                "mode": "table",
                "active_variant": ACTIVE_VARIANT.to_payload(),
                "agent": "random",
                "winner": "player_1",
                "turns": 20,
                "eliminations": ["player_0"],
                "final_populations": {"player_0": 0, "player_1": 30},
                "termination_reason": "one_player_remaining",
            }
        ],
        "summary": {
            "termination_counts": {"one_player_remaining": 1},
            "winner_counts": {"player_1": 1},
            "average_turns": 20.0,
            "total_eliminations": 1,
        },
    }
