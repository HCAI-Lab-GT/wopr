"""Source evidence capture packet tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from nuclear_war_env.card_effect_evidence import (
    CARD_EFFECT_EVIDENCE_PATH,
    validate_card_effect_evidence_manifest,
)
from nuclear_war_env.cards_registry import load_card_registry
from nuclear_war_env.expansion_composition_evidence import (
    EXPANSION_COMPOSITION_EVIDENCE_PATH,
    validate_expansion_composition_evidence_manifest,
)
from nuclear_war_env.expansions import EXPANSION_MECHANICS
from nuclear_war_env.rules import RULES_PATH

SOURCE_EVIDENCE_DIR = Path("research/source_evidence")
CARD_TEMPLATE = SOURCE_EVIDENCE_DIR / "card_effect_evidence.template.jsonl"
EXPANSION_TEMPLATE = SOURCE_EVIDENCE_DIR / ("expansion_deck_composition.template.jsonl")
CAPTURE_RUNBOOK = SOURCE_EVIDENCE_DIR / "CAPTURE_RUNBOOK.md"
CAPTURE_CHECKLIST = SOURCE_EVIDENCE_DIR / "CAPTURE_CHECKLIST.md"
PUBLIC_SOURCE_LEADS = SOURCE_EVIDENCE_DIR / "PUBLIC_SOURCE_LEADS.md"
SOURCE_INDEX = Path(
    "research/imports/2026-06-14_nuclear_war_card_game_research_bundle/"
    "source_index.json"
)
OFFICIAL_PUBLIC_LEAD_IDS = ("OFF-001", "OFF-002", "OFF-003", "OFF-004")


def test_capture_packet_documents_live_manifest_boundary() -> None:
    readme = (SOURCE_EVIDENCE_DIR / "README.md").read_text(encoding="utf-8")
    readme_lower = readme.lower()

    assert "card_effect_evidence.jsonl" in readme
    assert "expansion_deck_composition.jsonl" in readme
    assert "template files are not evidence" in readme
    assert "Do not include exact card text" in readme
    assert "validate-source-evidence" in readme
    assert "source-evidence-targets" in readme
    assert "source-evidence-draft-stubs" in readme
    assert "card_effect_evidence_target_details" in readme
    assert "coverage" in readme
    assert "not source evidence" in readme
    assert "live manifest validation requires" in readme_lower
    assert "second-pass verified" in readme_lower
    assert "CAPTURE_RUNBOOK.md" in readme
    assert "CAPTURE_CHECKLIST.md" in readme
    assert "PUBLIC_SOURCE_LEADS.md" in readme


def test_capture_runbook_documents_source_acquisition_workflow() -> None:
    runbook = CAPTURE_RUNBOOK.read_text(encoding="utf-8")
    runbook_lower = runbook.lower()

    assert "exact_text_gap_list.md" in runbook
    assert "private/" in runbook
    assert "card_effect_evidence.jsonl" in runbook
    assert "expansion_deck_composition.jsonl" in runbook
    assert "validate-source-evidence" in runbook
    assert "source-evidence-targets" in runbook
    assert "source-evidence-draft-stubs" in runbook
    assert "target-detail payloads" in runbook
    assert "coverage" in runbook
    assert "missing_ids" in runbook
    assert "second-pass" in runbook
    assert "live manifest validation fails" in runbook_lower
    assert "separate registry-change branch" in runbook
    assert "CAPTURE_CHECKLIST.md" in runbook
    assert "PUBLIC_SOURCE_LEADS.md" in runbook


def test_public_source_leads_inventory_is_public_safe() -> None:
    text = PUBLIC_SOURCE_LEADS.read_text(encoding="utf-8")
    text_lower = text.lower()

    assert "not source evidence" in text_lower
    assert "does not create live manifests" in text_lower
    assert "source_index.json" in text
    for source_id in ("OFF-001", "OFF-002", "OFF-003", "OFF-004"):
        assert source_id in text
    assert (
        "https://www.mrbgames.com/products/pre-order-nuclear-destruction-card-game"
        in text
    )
    assert "NucDesRulesUpdated040226.pdf" in text
    assert "NuclearDestructionLog.pdf" in text
    assert "Nuclear_DestructionAntiMissileChart.pdf" in text
    assert "do not clear" in text_lower
    assert "validate-source-evidence" in text
    assert "second-pass verified" in text_lower


def test_public_source_leads_match_imported_source_index() -> None:
    text = PUBLIC_SOURCE_LEADS.read_text(encoding="utf-8")
    entries = json.loads(SOURCE_INDEX.read_text(encoding="utf-8"))
    official_entries = [
        entry
        for entry in entries
        if isinstance(entry, dict) and entry.get("id") in OFFICIAL_PUBLIC_LEAD_IDS
    ]

    assert len(official_entries) == len(OFFICIAL_PUBLIC_LEAD_IDS)
    for entry in official_entries:
        source_id = entry["id"]
        url = entry["url"]
        assert isinstance(source_id, str)
        assert isinstance(url, str)
        assert source_id in text
        assert url in text


def test_capture_checklist_lists_current_source_targets() -> None:
    registry = load_card_registry(RULES_PATH)
    checklist = CAPTURE_CHECKLIST.read_text(encoding="utf-8")

    assert "not source evidence" in checklist
    assert "source-evidence-targets" in checklist
    assert "target-detail payloads" in checklist
    assert "Do not include exact card text" in checklist
    for record in registry.values():
        if record.count > 0:
            assert record.identifier in checklist
    for mechanic in EXPANSION_MECHANICS:
        assert mechanic.registry_id in checklist


def test_capture_templates_are_not_live_manifest_paths() -> None:
    assert CARD_TEMPLATE.name != CARD_EFFECT_EVIDENCE_PATH.name
    assert EXPANSION_TEMPLATE.name != EXPANSION_COMPOSITION_EVIDENCE_PATH.name


def test_private_capture_path_is_git_ignored() -> None:
    ignored_path = SOURCE_EVIDENCE_DIR / "private/source-capture/card-front.jpg"
    result = subprocess.run(
        ["git", "check-ignore", str(ignored_path)],
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert str(ignored_path) in result.stdout


def test_card_effect_template_is_public_safe_draft() -> None:
    registry = load_card_registry(RULES_PATH)

    result = validate_card_effect_evidence_manifest(
        CARD_TEMPLATE,
        known_card_ids=set(registry),
    )

    assert result.status == "present"
    assert result.record_count == 1
    assert result.verified_record_count == 0
    assert result.errors == []


def test_expansion_composition_template_is_public_safe_draft() -> None:
    result = validate_expansion_composition_evidence_manifest(EXPANSION_TEMPLATE)

    assert result.status == "present"
    assert result.record_count == 1
    assert result.verified_record_count == 0
    assert result.errors == []
