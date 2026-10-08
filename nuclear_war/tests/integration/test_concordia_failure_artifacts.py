"""Concordia strict failure artifact tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main


def test_cli_concordia_demo_writes_failure_snapshot_only(tmp_path, capsys) -> None:
    config_path = tmp_path / "config.json"
    out_dir = tmp_path / "out"
    config_path.write_text(json.dumps(_bad_config()), encoding="utf-8")

    code = main(
        [
            "concordia-demo",
            "--config",
            str(config_path),
            "--out-dir",
            str(out_dir),
        ]
    )

    captured = capsys.readouterr()
    snapshot_path = out_dir / "concordia" / "failure_snapshot.json"
    snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert code == 2
    assert json.loads(captured.out)["failure_snapshot_path"] == str(snapshot_path)
    assert snapshot["decision_failure"]["raw_visible_responses"] == ["not-json"]
    assert not (out_dir / "wopr" / "replay.json").exists()
    assert not (out_dir / "wopr" / "traces.json").exists()


def _bad_config() -> dict[str, object]:
    return {
        "players": 4,
        "seed": 71,
        "max_turns": 1,
        "runtime": "auto",
        "seats": {
            f"player_{index}": {
                "agent": "concordia_scripted",
                "identity": {"name": f"Commander {index}"},
                "scripted_responses": ["not-json"],
                "max_retries": 0,
            }
            for index in range(4)
        },
    }
