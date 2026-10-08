"""Concordia response parsing tests."""

from __future__ import annotations

import pytest

from nuclear_war_concordia.response import parse_concordia_response


def test_parse_concordia_response_reads_json_action_and_rationale() -> None:
    parsed = parse_concordia_response(
        '{"action_id": "player_0:draw", "rationale": "maintain tempo"}'
    )

    assert parsed.action_id == "player_0:draw"
    assert parsed.rationale == "maintain tempo"


def test_parse_concordia_response_reads_fenced_json_action() -> None:
    parsed = parse_concordia_response(
        '```json\n{"action_id": "player_0:draw", "rationale": "draw now"}\n```'
    )

    assert parsed.action_id == "player_0:draw"
    assert parsed.rationale == "draw now"


@pytest.mark.parametrize(
    "raw_response",
    [
        '{"action_id": 17, "rationale": "use the numeric action"}',
        '{"action_id": "", "rationale": "use the empty action"}',
        '{"rationale": "choose from context"}',
    ],
)
def test_parse_concordia_response_rejects_invalid_action_with_rationale(
    raw_response: str,
) -> None:
    parsed = parse_concordia_response(raw_response)

    assert parsed.action_id is None
    assert parsed.rationale is None
