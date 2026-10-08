"""CLI replay strict JSON parsing tests."""

from __future__ import annotations

from nuclear_war_env.cli import main


def test_cli_replay_rejects_nan_constant_as_malformed_json(tmp_path, capsys) -> None:
    malformed = tmp_path / "nan_replay.json"
    malformed.write_text(
        """
{
  "mode": "table",
  "active_variant": {},
  "seed": NaN,
  "agent": "heuristic",
  "players": 2,
  "winner": null,
  "turns": 1,
  "termination_reason": "max_turns",
  "eliminations": [],
  "final_populations": {"player_0": 30, "player_1": 30},
  "actions": [],
  "events": []
}
""",
        encoding="utf-8",
    )

    code = main(["replay", str(malformed)])

    captured = capsys.readouterr()
    assert code == 2
    assert "Replay file is not valid JSON" in captured.err
