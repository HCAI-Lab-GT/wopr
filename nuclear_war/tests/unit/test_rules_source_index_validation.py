"""Rule validation source-index tests."""

from __future__ import annotations

import json
from pathlib import Path

from nuclear_war_env.rules import validate_rules
from nuclear_war_env.source_validation import SOURCE_INDEX_PATH


def test_validate_rules_rejects_malformed_source_index(tmp_path: Path) -> None:
    source_index_path = tmp_path / "source_index.json"
    source_index_path.write_text("{bad json", encoding="utf-8")

    payload = validate_rules(source_index_path=source_index_path)

    assert payload["ok"] is False
    assert payload["source_index_errors"] == [
        {"path": str(source_index_path), "error": "malformed_json"}
    ]


def test_validate_rules_rejects_source_index_json_constants(
    tmp_path: Path,
) -> None:
    source_index_path = tmp_path / "source_index.json"
    source_index_path.write_text('[{"id": NaN}]', encoding="utf-8")

    payload = validate_rules(source_index_path=source_index_path)

    assert payload["ok"] is False
    assert payload["source_index_errors"] == [
        {"path": str(source_index_path), "error": "malformed_json"}
    ]


def test_validate_rules_rejects_source_index_entries_without_ids(
    tmp_path: Path,
) -> None:
    entries = json.loads(SOURCE_INDEX_PATH.read_text(encoding="utf-8"))
    entries.append({"title": "Missing source identifier"})
    source_index_path = tmp_path / "source_index.json"
    source_index_path.write_text(json.dumps(entries), encoding="utf-8")

    payload = validate_rules(source_index_path=source_index_path)

    assert payload["ok"] is False
    assert payload["source_index_errors"] == [
        {
            "path": str(source_index_path),
            "error": "invalid_entry_id",
            "line": "35",
        }
    ]


def test_validate_rules_rejects_source_index_ids_with_outer_whitespace(
    tmp_path: Path,
) -> None:
    entries = json.loads(SOURCE_INDEX_PATH.read_text(encoding="utf-8"))
    entries.append({"id": " spaced_source ", "title": "Whitespace source"})
    source_index_path = tmp_path / "source_index.json"
    source_index_path.write_text(json.dumps(entries), encoding="utf-8")

    payload = validate_rules(source_index_path=source_index_path)

    assert payload["ok"] is False
    assert payload["source_index_errors"] == [
        {
            "path": str(source_index_path),
            "error": "invalid_entry_id",
            "line": "35",
        }
    ]


def test_validate_rules_rejects_source_index_ids_outside_ledger_shape(
    tmp_path: Path,
) -> None:
    entries = json.loads(SOURCE_INDEX_PATH.read_text(encoding="utf-8"))
    entries.append({"id": "comm-999", "title": "Lowercase source"})
    source_index_path = tmp_path / "source_index.json"
    source_index_path.write_text(json.dumps(entries), encoding="utf-8")

    payload = validate_rules(source_index_path=source_index_path)

    assert payload["ok"] is False
    assert payload["source_index_id_count"] == len(entries) - 1
    assert payload["source_index_errors"] == [
        {
            "path": str(source_index_path),
            "error": "invalid_entry_id",
            "line": "35",
        }
    ]


def test_validate_rules_rejects_duplicate_source_index_ids(
    tmp_path: Path,
) -> None:
    entries = json.loads(SOURCE_INDEX_PATH.read_text(encoding="utf-8"))
    entries.append(dict(entries[0]))
    source_index_path = tmp_path / "source_index.json"
    source_index_path.write_text(json.dumps(entries), encoding="utf-8")

    payload = validate_rules(source_index_path=source_index_path)

    assert payload["ok"] is False
    assert payload["source_index_errors"] == [
        {
            "path": str(source_index_path),
            "error": "duplicate_entry_id",
            "source_id": entries[0]["id"],
            "first_line": "1",
            "duplicate_line": "35",
        }
    ]
