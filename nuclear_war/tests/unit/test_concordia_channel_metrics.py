"""Channel-separated Concordia call and usage metrics tests."""

from nuclear_war_agents import LLMCompletion
from nuclear_war_concordia.channel_metrics import build_channel_metrics
from nuclear_war_concordia.press_trace import append_press_trace
from nuclear_war_concordia.types import ConcordiaScene, ParsedPressMessage


def test_channel_metrics_separate_calls_retries_and_provider_usage() -> None:
    strategic = [_trace(["a", "b"], {"input_tokens": 3}, recoverable=1)]
    c2_artifact = {
        "deliberations": [
            {
                "members": [
                    {"trace": _trace(["c"], {"input_tokens": 5})},
                    {"trace": _trace(["d"], {"output_tokens": 2})},
                    {"trace": _trace(["e"], None)},
                ]
            }
        ]
    }
    press = [_trace(["f"], {"output_tokens": 7})]

    metrics = build_channel_metrics(strategic, c2_artifact, press)

    assert metrics["strategic"]["call_count"] == 3
    assert metrics["strategic"]["provider_usage"] == {"input_tokens": 3}
    assert metrics["c2"]["call_count"] == 3
    assert metrics["c2"]["provider_usage"] == {
        "input_tokens": 5,
        "output_tokens": 2,
    }
    assert "provider_cost" not in metrics["c2"]
    assert "provider_latency_ms" not in metrics["c2"]
    assert metrics["press"]["call_count"] == 1
    assert metrics["press"]["provider_usage"] == {"output_tokens": 7}


def test_press_channel_counts_transport_retries_from_press_trace() -> None:
    press_traces: list[dict] = []
    response = '{"action_id": "decline"}'
    append_press_trace(
        press_sink=press_traces,
        round_no=1,
        speaker="player_0",
        audience="public",
        visibility="public",
        pass_no=1,
        prior_messages=[],
        scene=ConcordiaScene(text="scene", payload={"turn": 1}),
        prompts=["prompt"],
        raw_responses=[response],
        completions=[
            LLMCompletion(raw_response=response, provider_transport_retries=2)
        ],
        validation_errors=[],
        parsed=ParsedPressMessage(declined=True),
    )

    metrics = build_channel_metrics([], None, press_traces)

    assert press_traces[0]["recoverable_provider_retries"] == 2
    assert metrics["press"]["recoverable_provider_retry_count"] == 2
    assert metrics["press"]["call_count"] == 3


def _trace(
    responses: list[str],
    usage: dict[str, int] | None,
    *,
    recoverable: int = 0,
) -> dict[str, object]:
    return {
        "raw_responses": responses,
        "retries": max(0, len(responses) - 1),
        "recoverable_provider_retries": recoverable,
        "provider_usage": usage,
        "provider_latency_ms": None,
        "provider_cost": None,
    }
