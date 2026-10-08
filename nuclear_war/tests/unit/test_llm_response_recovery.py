from __future__ import annotations

from nuclear_war_agents import parse_llm_response


def test_parse_llm_response_reads_fenced_json_action() -> None:
    parsed = parse_llm_response(
        '```json\n{"action_id": "smoke:test", "rationale": "ok"}\n```'
    )

    assert parsed.action_id == "smoke:test"
    assert parsed.rationale == "ok"


def test_parse_llm_response_recovers_quoted_action_from_partial_json() -> None:
    parsed = parse_llm_response(
        '{"action_id": "player_0:secret_target:{\\"card\\":\\"c1\\",'
        '\\"target\\":\\"player_2\\"}", "rationale": "cut off"'
    )

    assert parsed.action_id == (
        'player_0:secret_target:{"card":"c1","target":"player_2"}'
    )


def test_parse_llm_response_recovers_verbatim_legal_action() -> None:
    legal = 'player_0:secret_target:{"card":"c1","target":"player_2"}'
    parsed = parse_llm_response(
        '{"action_id": "player_0:secret_target:{"card":"c1",'
        '"target":"player_2"}", "rationale": "ok"}',
        [legal],
    )

    assert parsed.action_id == legal
