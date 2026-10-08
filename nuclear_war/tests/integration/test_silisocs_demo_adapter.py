"""SiliSocs demo adapter artifact tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main
from nuclear_war_env.llm_harness_batch import load_no_press_llm_batch_config
from nuclear_war_env.llm_trace_artifacts import read_trace_artifact
from nuclear_war_env.replay import read_replay
from nuclear_war_silisocs.backend import NuclearWarNoPressBackend
from nuclear_war_silisocs.demo import run_silisocs_no_press_demo


def test_silisocs_demo_writes_wopr_artifacts_and_metadata(tmp_path) -> None:
    config = load_no_press_llm_batch_config(_scripted_config())

    result = run_silisocs_no_press_demo(
        config,
        tmp_path,
        scenario_name="nuclear_war_no_press",
    )

    replay_path = tmp_path / "wopr" / "replay.json"
    trace_path = tmp_path / "wopr" / "traces.json"
    summary_path = tmp_path / "wopr" / "summary.json"
    config_path = tmp_path / "silisocs" / "config_snapshot.json"
    telemetry_path = tmp_path / "silisocs" / "telemetry.json"

    replay = read_replay(replay_path)
    trace = read_trace_artifact(trace_path, replay)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    snapshot = json.loads(config_path.read_text(encoding="utf-8"))
    telemetry = json.loads(telemetry_path.read_text(encoding="utf-8"))

    assert result["replay_path"] == replay_path
    assert trace["replay"]["seed"] == replay["seed"]
    assert summary["trace_count"] == len(trace["traces"])
    assert snapshot["seats"]["player_0"]["agent"] == "llm_scripted"
    assert telemetry["scenario_name"] == "nuclear_war_no_press"
    assert telemetry["runtime_contracts"]["backend"] == (
        "silisocs.environments.backends.base.BackendApp"
    )
    assert (tmp_path / "README.md").is_file()


def test_cli_silisocs_demo_writes_artifacts(tmp_path, capsys) -> None:
    config_path = tmp_path / "config.json"
    out_dir = tmp_path / "out"
    config_path.write_text(json.dumps(_scripted_config()), encoding="utf-8")

    code = main(
        [
            "silisocs-demo",
            "--config",
            str(config_path),
            "--out-dir",
            str(out_dir),
            "--scenario-name",
            "nuclear_war_no_press",
        ]
    )

    captured = capsys.readouterr()
    assert code == 0
    assert "replay_path" in captured.out
    assert (out_dir / "wopr" / "replay.json").is_file()


def test_silisocs_backend_can_trigger_demo_run(tmp_path) -> None:
    backend = NuclearWarNoPressBackend(
        config_payload=_scripted_config(),
        output_dir=str(tmp_path),
        scenario_name="nuclear_war_no_press",
    )

    backend.initialize(["player_0", "player_1", "player_2", "player_3"])
    result = backend.run_demo(agent_name="player_0")

    assert "wopr/replay.json" in result
    assert (tmp_path / "wopr" / "replay.json").is_file()
    assert "Nuclear War no-press" in backend.observe("player_0")


def _scripted_config() -> dict[str, object]:
    return {
        "players": 4,
        "seed_start": 31,
        "runs": 1,
        "max_turns": 1,
        "seats": {
            "player_0": {
                "agent": "llm_scripted",
                "scripted_responses": ['{"action_id": "player_0:draw"}'],
            },
            "player_1": {"agent": "random"},
            "player_2": {"agent": "heuristic"},
            "player_3": {"agent": "decision_heuristic"},
        },
    }
