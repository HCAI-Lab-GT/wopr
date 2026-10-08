"""Source evidence CLI commands."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .source_evidence_draft_stubs import draft_stub_jsonl
from .source_evidence_preflight import validate_source_evidence_files
from .source_evidence_targets import source_evidence_targets_payload


def add_source_evidence_parsers(subparsers: Any) -> None:
    source_evidence = subparsers.add_parser("validate-source-evidence")
    source_evidence.add_argument("--card-effects")
    source_evidence.add_argument("--expansion-composition")
    draft_stubs = subparsers.add_parser("source-evidence-draft-stubs")
    draft_stubs.add_argument(
        "--kind",
        choices=["card-effects", "expansion-composition"],
        required=True,
    )
    subparsers.add_parser("source-evidence-targets")


def run_source_evidence_command(args: argparse.Namespace) -> int | None:
    if args.command == "validate-source-evidence":
        payload = validate_source_evidence_files(
            card_effect_path=(Path(args.card_effects) if args.card_effects else None),
            expansion_composition_path=(
                Path(args.expansion_composition) if args.expansion_composition else None
            ),
        )
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["ok"] else 1
    if args.command == "source-evidence-targets":
        payload = source_evidence_targets_payload()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    if args.command == "source-evidence-draft-stubs":
        print(draft_stub_jsonl(args.kind), end="")
        return 0
    return None


__all__ = ["add_source_evidence_parsers", "run_source_evidence_command"]
