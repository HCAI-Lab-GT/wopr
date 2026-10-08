"""Rule validation duplicate identifier tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.rules import RULES_PATH, validate_rules


def test_validate_rules_rejects_duplicate_registry_ids(tmp_path: Path) -> None:
    records = [
        json.loads(line)
        for line in RULES_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    records.append(dict(records[0]))
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["duplicate_card_ids"] == [
        {"card_id": records[0]["id"], "first_line": 1, "duplicate_line": 41}
    ]


def test_validate_rules_reports_no_invalid_registry_ids() -> None:
    payload = validate_rules()
    assert payload["invalid_card_ids"] == []


def test_validate_rules_rejects_invalid_registry_type(tmp_path: Path) -> None:
    records = [
        json.loads(line)
        for line in RULES_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    records[0]["type"] = "orbital"
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["invalid_card_types"] == [
        {"line": 1, "card_id": records[0]["id"], "type": "orbital"}
    ]


def test_validate_rules_rejects_missing_registry_id(tmp_path: Path) -> None:
    records = [
        json.loads(line)
        for line in RULES_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    records[0].pop("id")
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["invalid_card_ids"] == [{"line": 1, "id": None}]


def test_validate_rules_rejects_missing_registry_name(tmp_path: Path) -> None:
    records = [
        json.loads(line)
        for line in RULES_PATH.read_text(encoding="utf-8").splitlines()
        if line
    ]
    records[0].pop("name")
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text(
        "\n".join(json.dumps(record) for record in records),
        encoding="utf-8",
    )

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["invalid_card_names"] == [
        {"card_id": records[0]["id"], "name": None}
    ]


def test_validate_rules_rejects_malformed_registry_json(tmp_path: Path) -> None:
    lines = RULES_PATH.read_text(encoding="utf-8").splitlines()
    lines[0] = "{bad json"
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text("\n".join(lines), encoding="utf-8")

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["malformed_registry_lines"] == [{"line": 1}]


def test_validate_rules_rejects_registry_json_constants(tmp_path: Path) -> None:
    lines = RULES_PATH.read_text(encoding="utf-8").splitlines()
    lines[0] = '{"id": NaN, "type": "warhead", "name": "Invalid"}'
    registry_path = tmp_path / "cards.jsonl"
    registry_path.write_text("\n".join(lines), encoding="utf-8")

    payload = validate_rules(registry_path)

    assert payload["ok"] is False
    assert payload["malformed_registry_lines"] == [{"line": 1}]
