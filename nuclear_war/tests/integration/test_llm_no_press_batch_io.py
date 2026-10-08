"""No-press LLM batch artifact IO tests."""

import json

import pytest

from nuclear_war_env import llm_harness_batch_stream
from nuclear_war_env.cli import main
from nuclear_war_env.llm_harness import LLMSeatConfig
from nuclear_war_env.llm_harness_batch import (
    NoPressLLMBatchConfig,
    run_no_press_llm_batch,
)
from nuclear_war_env.llm_harness_batch_io import (
    read_no_press_llm_batch,
    write_no_press_llm_batch,
)
from nuclear_war_env.llm_harness_batch_stream import run_no_press_llm_batch_to_dir
from nuclear_war_env.variants import ACTIVE_VARIANT_ID


def test_read_no_press_llm_batch_validates_linked_replays_and_traces(tmp_path) -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=4,
            seed_start=31,
            runs=2,
            max_turns=1,
            seats=_seat_configs(),
        )
    )
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)

    payload = read_no_press_llm_batch(summary_path)

    assert payload["summary"] == result["summary"]
    assert [item["seed"] for item in payload["results"]] == [31, 32]


def test_write_no_press_llm_batch_records_config_snapshot(tmp_path) -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=4,
            seed_start=31,
            runs=1,
            max_turns=1,
            seats={
                "player_0": LLMSeatConfig(
                    "llm_scripted",
                    scripted_responses=("not-json", '{"action_id": "player_0:draw"}'),
                    max_retries=2,
                    fallback="first",
                ),
                "player_1": LLMSeatConfig("random"),
                "player_2": LLMSeatConfig("heuristic"),
                "player_3": LLMSeatConfig("decision_heuristic"),
            },
        )
    )
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)

    config = read_no_press_llm_batch(summary_path)["config"]

    assert config["players"] == 4
    assert config["seed_start"] == 31
    assert config["runs"] == 1
    assert config["max_turns"] == 1
    assert config["variant_id"] == ACTIVE_VARIANT_ID
    assert config["seats"]["player_0"] == {
        "agent": "llm_scripted",
        "scripted_responses": ["not-json", '{"action_id": "player_0:draw"}'],
        "scripted_provider_latency_ms": [],
        "scripted_provider_cost": [],
        "max_retries": 2,
        "fallback": "first",
    }


def test_read_no_press_llm_batch_round_trips_faction_seat(tmp_path) -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=2,
            seed_start=7,
            runs=1,
            max_turns=3,
            seats={
                "player_0": LLMSeatConfig(
                    "faction_c2",
                    archetype="council",
                    archetype_parameters={"threshold": 0.5},
                    members=(
                        {"member_id": "advisor_a", "agent": "llm_first_legal"},
                        {"member_id": "advisor_b", "agent": "llm_first_legal"},
                    ),
                ),
                "player_1": LLMSeatConfig("heuristic"),
            },
        )
    )
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)

    payload = read_no_press_llm_batch(summary_path)

    player_0 = payload["config"]["seats"]["player_0"]
    assert player_0["archetype"] == "council"
    assert player_0["archetype_parameters"] == {"threshold": 0.5}
    assert player_0["members"] == [
        {"member_id": "advisor_a", "agent": "llm_first_legal"},
        {"member_id": "advisor_b", "agent": "llm_first_legal"},
    ]


def test_read_no_press_llm_batch_rejects_trace_without_replay_link(tmp_path) -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=4,
            seed_start=31,
            runs=1,
            max_turns=1,
            seats=_seat_configs(),
        )
    )
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)
    trace_path = summary_path.parent / "seed-31.replay.traces.json"
    trace_payload = json.loads(trace_path.read_text(encoding="utf-8"))
    trace = trace_payload["traces"][0]
    trace["selected_action_id"] = "missing-action"
    # Insert at the front so the fabricated id is options[0] — a legitimate
    # "first"-policy fallback target — which passes legal-option validation and
    # isolates the replay-link check below (the id links to no replay action).
    trace["legal_options"].insert(0, {"action_id": "missing-action"})
    trace["rendered_observation"]["decision"]["options"] = trace["legal_options"]
    trace_path.write_text(json.dumps(trace_payload), encoding="utf-8")

    with pytest.raises(ValueError, match="selected_action_id does not link"):
        read_no_press_llm_batch(summary_path)


def test_read_no_press_llm_batch_rejects_seed_sequence_mismatch(tmp_path) -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=4,
            seed_start=31,
            runs=1,
            max_turns=1,
            seats=_seat_configs(),
        )
    )
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    payload["seed_start"] = 30
    payload["config"]["seed_start"] = 30
    summary_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="seed does not match seed_start"):
        read_no_press_llm_batch(summary_path)


def test_cli_llm_summarize_validates_batch_summary(tmp_path, capsys) -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=4,
            seed_start=31,
            runs=1,
            max_turns=1,
            seats=_seat_configs(),
        )
    )
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)

    code = main(["llm-summarize", str(summary_path)])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["runs"] == 1
    assert payload["total_trace_count"] >= 1


def test_run_no_press_llm_batch_to_dir_matches_eager_write(tmp_path) -> None:
    config = NoPressLLMBatchConfig(
        players=4,
        seed_start=31,
        runs=2,
        max_turns=1,
        seats=_seat_configs(),
    )

    stream_dir = tmp_path / "stream"
    stream_summary = run_no_press_llm_batch_to_dir(stream_dir, config)

    eager_dir = tmp_path / "eager"
    eager_summary = write_no_press_llm_batch(eager_dir, run_no_press_llm_batch(config))

    # The successful streamed batch must be byte-identical to the eager path.
    assert stream_summary.read_text(encoding="utf-8") == eager_summary.read_text(
        encoding="utf-8"
    )
    for name in ("seed-31.replay.json", "seed-31.replay.traces.json"):
        assert (stream_dir / name).read_text(encoding="utf-8") == (
            eager_dir / name
        ).read_text(encoding="utf-8")
    # And it still validates on read.
    read_no_press_llm_batch(stream_summary)
    assert not (stream_dir / "failure_marker.json").exists()


def test_run_no_press_llm_batch_to_dir_writes_partial_and_failure_marker(
    tmp_path, monkeypatch
) -> None:
    real_run_game = llm_harness_batch_stream.run_no_press_llm_game
    calls = {"n": 0}

    def flaky(game_config):
        calls["n"] += 1
        if calls["n"] == 2:
            raise RuntimeError("boom at game 2")
        return real_run_game(game_config)

    monkeypatch.setattr(llm_harness_batch_stream, "run_no_press_llm_game", flaky)
    out_dir = tmp_path / "out"

    with pytest.raises(ValueError, match="aborted at seed 32"):
        run_no_press_llm_batch_to_dir(
            out_dir,
            NoPressLLMBatchConfig(
                players=4,
                seed_start=31,
                runs=3,
                max_turns=1,
                seats=_seat_configs(),
            ),
        )

    # The first game completed and its artifacts are on disk.
    assert (out_dir / "seed-31.replay.json").exists()
    assert (out_dir / "seed-31.replay.traces.json").exists()
    # The aborted game left no artifacts, and no summary.json was written.
    assert not (out_dir / "seed-32.replay.json").exists()
    assert not (out_dir / "summary.json").exists()
    # A deterministic failure marker records where the batch stopped.
    marker = json.loads((out_dir / "failure_marker.json").read_text(encoding="utf-8"))
    assert marker["status"] == "aborted"
    assert marker["requested_runs"] == 3
    assert marker["completed_runs"] == 1
    assert marker["failed_seed"] == 32
    assert "boom at game 2" in marker["error"]
    assert [item["seed"] for item in marker["results"]] == [31]


def _seat_configs() -> dict[str, LLMSeatConfig]:
    return {
        "player_0": LLMSeatConfig(
            "llm_scripted",
            scripted_responses=("not-json", '{"action_id": "player_0:draw"}'),
        ),
        "player_1": LLMSeatConfig("random"),
        "player_2": LLMSeatConfig("heuristic"),
        "player_3": LLMSeatConfig("decision_heuristic"),
    }
