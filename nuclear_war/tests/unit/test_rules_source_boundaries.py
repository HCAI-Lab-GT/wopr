"""Rule source-boundary validation tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.rules import RULES_PATH, validate_rules


def test_validate_rules_rejects_nested_restricted_text_fields(
    tmp_path: Path,
) -> None:
    records = [
        json.loads(line)
        for line in RULES_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    records[0]["metadata"] = {"exact_text": "restricted"}
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["restricted_text_fields"] == [
        {"card_id": records[0]["id"], "field": "metadata.exact_text"}
    ]
