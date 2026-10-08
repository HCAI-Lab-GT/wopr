"""Scriptable CLI for Nuclear War v1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import replay, source_evidence_cli
from .cli_parser import build_parser
from .experiments import ExperimentConfig, run_experiment
from .live_api_server import run_live_api_server
from .llm_harness_cli import run_llm_harness_command
from .llm_model_scorecard_cli import run_model_scorecard_command
from .local_env import load_local_dotenv
from .rules import validate_rules
from .simulation import SimulationConfig, run_simulation


def main(argv: list[str] | None = None) -> int:
    load_local_dotenv()
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        return _run_command(args, parser)
    except SystemExit as exc:
        if argv is None:
            raise
        return exc.code if isinstance(exc.code, int) else 2
    except ValueError as exc:
        print(f"{parser.prog}: error: {exc}", file=sys.stderr)
        return 2


def _run_command(args: argparse.Namespace, parser: argparse.ArgumentParser) -> int:
    if args.command == "validate-rules":
        payload = validate_rules()
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0 if payload["ok"] else 1
    source_evidence_code = source_evidence_cli.run_source_evidence_command(args)
    if source_evidence_code is not None:
        return source_evidence_code
    llm_harness_code = run_llm_harness_command(args)
    if llm_harness_code is not None:
        return llm_harness_code
    model_scorecard_code = run_model_scorecard_command(args)
    if model_scorecard_code is not None:
        return model_scorecard_code
    if args.command == "simulate":
        replay.validate_replay_output_path(Path(args.out))
        payload = run_simulation(
            SimulationConfig(
                mode=args.mode,
                players=args.players,
                seed=args.seed,
                agent=args.agent,
                max_turns=args.max_turns,
                press=False,
                variant_id=args.variant,
            )
        )
        replay.write_replay(Path(args.out), payload)
        print(json.dumps(replay.summarize_replay(payload), indent=2, sort_keys=True))
        return 0
    if args.command == "live-server":
        run_live_api_server(
            host=args.host,
            port=args.port,
            players=args.players,
            seed=args.seed,
            max_turns=args.max_turns,
            controlled_players=tuple(args.controlled or ("player_0",)),
        )
        return 0
    if args.command == "experiment":
        replay.validate_replay_output_path(Path(args.out))
        payload = run_experiment(
            ExperimentConfig(
                mode=args.mode,
                players=args.players,
                seed_start=args.seed_start,
                runs=args.runs,
                agent=args.agent,
                max_turns=args.max_turns,
                press=False,
                variant_id=args.variant,
            )
        )
        replay.write_replay(Path(args.out), payload)
        print(json.dumps(payload["summary"], indent=2, sort_keys=True))
        return 0
    if args.command == "replay":
        print(json.dumps(replay.read_replay(Path(args.path)), indent=2, sort_keys=True))
        return 0
    if args.command == "summarize":
        payload = replay.summarize_replay(replay.read_replay(Path(args.path)))
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
