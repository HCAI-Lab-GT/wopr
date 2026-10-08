"""Concordia demo artifact tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_concordia.artifacts import write_concordia_no_press_artifacts
from nuclear_war_concordia.config import load_concordia_no_press_config
from nuclear_war_concordia.harness import run_concordia_no_press_game
from nuclear_war_env.cli import main
from nuclear_war_env.llm_trace_artifacts import read_trace_artifact
from nuclear_war_env.replay import read_replay


def test_write_concordia_no_press_artifacts(tmp_path) -> None:
    config = load_concordia_no_press_config(_config())
    result = run_concordia_no_press_game(config)
    expected_paths = _expected_paths(tmp_path)

    paths = write_concordia_no_press_artifacts(tmp_path, result)

    assert set(paths) == set(expected_paths)
    assert paths == expected_paths
    replay = read_replay(paths["replay_path"])
    trace = read_trace_artifact(paths["trace_path"], replay)
    summary = json.loads(paths["summary_path"].read_text(encoding="utf-8"))
    metadata = json.loads(paths["agent_metadata_path"].read_text(encoding="utf-8"))
    c2_artifact = json.loads(paths["c2_path"].read_text(encoding="utf-8"))

    assert trace["replay"]["seed"] == replay["seed"]
    assert summary["trace_count"] == len(trace["traces"])
    assert metadata["player_0"]["identity"]["name"] == "Commander 0"
    assert c2_artifact["authority_players"] == []
    assert c2_artifact["deliberations"] == []


def test_cli_concordia_demo_writes_artifacts(tmp_path, capsys) -> None:
    config_path = tmp_path / "config.json"
    out_dir = tmp_path / "out"
    config_path.write_text(json.dumps(_config()), encoding="utf-8")

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
    expected_paths = _expected_paths(out_dir)
    payload = json.loads(captured.out)
    assert code == 0
    assert payload == {key: str(path) for key, path in expected_paths.items()}
    assert all(path.is_file() for path in expected_paths.values())


def _expected_paths(out_dir: Path) -> dict[str, Path]:
    return {
        "replay_path": out_dir / "wopr" / "replay.json",
        "trace_path": out_dir / "wopr" / "traces.json",
        "c2_path": out_dir / "concordia" / "c2_deliberations.json",
        "summary_path": out_dir / "concordia" / "run_summary.json",
        "config_path": out_dir / "concordia" / "config_snapshot.json",
        "agent_metadata_path": out_dir / "concordia" / "agent_metadata.json",
        "runtime_path": out_dir / "concordia" / "runtime_status.json",
    }


def _config() -> dict[str, object]:
    return {
        "players": 4,
        "seed": 71,
        "max_turns": 1,
        "runtime": "auto",
        "seats": {
            f"player_{index}": {
                "agent": "concordia_first_legal",
                "identity": {
                    "name": f"Commander {index}",
                    "role": "strategic actor",
                    "objective": "survive the game",
                },
            }
            for index in range(4)
        },
    }
