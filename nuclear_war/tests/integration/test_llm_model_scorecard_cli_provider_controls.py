from __future__ import annotations

import json

from nuclear_war_agents import LLMHttpClient
from nuclear_war_env import llm_model_scorecard_cli as scorecard_cli
from nuclear_war_env.cli import main
from nuclear_war_env.llm_model_scorecard_stage2_support import Stage2ModelResult


def test_cli_stage2_together_accepts_provider_controls(
    tmp_path,
    monkeypatch,
) -> None:
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(
        json.dumps({"chat": [{"id": "demo/model", "name": "Demo"}]}),
        encoding="utf-8",
    )
    out_dir = tmp_path / "scorecard"
    seen: dict[str, object] = {}

    def fake_run_stage2_model(config, model_id, client_factory):
        seen["client"] = client_factory(model_id)
        return Stage2ModelResult(
            model_id=model_id,
            status="passed",
            direct_smoke_passed=True,
            wopr_one_turn_passed=True,
            trace_count=0,
            invalid_action_count=0,
            retry_count=0,
            selected_action_ids=(),
            provider_usage=None,
            provider_latency_ms=None,
            error_type=None,
            error_message=None,
        )

    monkeypatch.setattr(scorecard_cli, "run_stage2_model", fake_run_stage2_model)

    code = main(
        [
            "llm-model-scorecard",
            "--catalog",
            str(catalog_path),
            "--out",
            str(out_dir),
            "--stage",
            "stage2",
            "--provider",
            "together",
            "--max-models-cost-usd",
            "0.50",
            "--disable-reasoning",
            "--stream",
        ]
    )

    client = seen["client"]
    assert code == 0
    assert isinstance(client, LLMHttpClient)
    assert client.config.reasoning_enabled is False
    assert client.config.stream is True
