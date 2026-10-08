from __future__ import annotations

from nuclear_war_agents.llm_http_response import message_content, response_json


def test_message_content_uses_choice_text_fallback() -> None:
    payload = {
        "choices": [
            {
                "text": '{"action_id": "smoke:test"}',
                "message": {"content": None},
            }
        ]
    }

    assert message_content(payload) == '{"action_id": "smoke:test"}'


def test_response_json_aggregates_streaming_delta_content() -> None:
    payload = response_json(
        'data: {"choices":[{"delta":{"content":"{\\"action_id\\": "}}]}\n\n'
        'data: {"choices":[{"delta":{"content":"\\"smoke:test\\"}"}}]}\n\n'
        "data: [DONE]\n\n"
    )

    assert message_content(payload) == '{"action_id": "smoke:test"}'
