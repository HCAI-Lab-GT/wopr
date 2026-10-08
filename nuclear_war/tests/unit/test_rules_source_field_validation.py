"""Rule source-field validation tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.rules import RULES_PATH, validate_rules


def test_validate_rules_rejects_non_string_source_entries(tmp_path: Path) -> None:
    records = [
        json.loads(line)
        for line in RULES_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    records[0]["sources"] = [123]
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["invalid_source_fields"] == [
        {"card_id": records[0]["id"], "source": 123}
    ]


def test_validate_rules_rejects_source_ids_outside_ledger_shape(
    tmp_path: Path,
) -> None:
    records = [
        json.loads(line)
        for line in RULES_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    records[0]["sources"] = ["comm-999"]
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["invalid_source_fields"] == [
        {"card_id": records[0]["id"], "source": "comm-999"}
    ]


def test_validate_rules_rejects_non_list_sources_field(tmp_path: Path) -> None:
    records = [
        json.loads(line)
        for line in RULES_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    records[0]["sources"] = "COMM-001"
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["invalid_source_fields"] == [
        {"card_id": records[0]["id"], "source": "COMM-001"}
    ]
