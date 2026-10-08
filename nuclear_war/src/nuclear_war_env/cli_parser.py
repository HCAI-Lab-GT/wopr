"""Argument parser construction for the Nuclear War CLI."""

from __future__ import annotations

import argparse

from .agent_names import SIMULATION_AGENT_NAMES
from .llm_harness_cli import add_llm_harness_parser
from .llm_model_scorecard_cli import add_model_scorecard_parser
from .source_evidence_cli import add_source_evidence_parsers
from .variant_catalog import known_variant_ids
from .variants import ACTIVE_VARIANT_ID


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nuclear-war")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate-rules")
    add_source_evidence_parsers(subparsers)
    variant_choices = known_variant_ids()
    variant_kwargs = {"choices": variant_choices, "default": ACTIVE_VARIANT_ID}
    _add_simulate_parser(subparsers, variant_kwargs)
    _add_live_server_parser(subparsers)
    _add_experiment_parser(subparsers, variant_kwargs)
    add_llm_harness_parser(subparsers)
    add_model_scorecard_parser(subparsers)
    replay = subparsers.add_parser("replay")
    replay.add_argument("path")
    summarize = subparsers.add_parser("summarize")
    summarize.add_argument("path")
    return parser


def _add_simulate_parser(subparsers, variant_kwargs) -> None:
    parser = subparsers.add_parser("simulate")
    parser.add_argument("--mode", choices=["table", "postal"], required=True)
    parser.add_argument("--players", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--agent", choices=SIMULATION_AGENT_NAMES, required=True)
    parser.add_argument("--max-turns", type=int, default=50)
    parser.add_argument("--variant", **variant_kwargs)
    parser.add_argument("--out", required=True)


def _add_live_server_parser(subparsers) -> None:
    parser = subparsers.add_parser("live-server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--players", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-turns", type=int, default=50)
    parser.add_argument("--controlled", action="append")


def _add_experiment_parser(subparsers, variant_kwargs) -> None:
    parser = subparsers.add_parser("experiment")
    parser.add_argument("--mode", choices=["table", "postal"], required=True)
    parser.add_argument("--players", type=int, required=True)
    parser.add_argument("--seed-start", type=int, required=True)
    parser.add_argument("--runs", type=int, required=True)
    parser.add_argument("--agent", choices=SIMULATION_AGENT_NAMES, required=True)
    parser.add_argument("--max-turns", type=int, default=50)
    parser.add_argument("--variant", **variant_kwargs)
    parser.add_argument("--out", required=True)


__all__ = ["build_parser"]
