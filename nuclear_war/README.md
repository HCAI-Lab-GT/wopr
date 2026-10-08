# Nuclear War

A deterministic, replay-validated implementation of the *Nuclear War* card game,
used as the rules engine for the WOPR social-simulation environment. Language
model agents, the Concordia press ladder, and collective command-and-control
factions are layered on top of the same engine.

## Install

Python 3.13 and [`uv`](https://docs.astral.sh/uv/) are required. Commands below
run from this directory.

```bash
uv sync --extra dev
```

The `dev` extra includes the `concordia` extra (`gdm-concordia`), so the native
Concordia harness is installed and tested by default. `silisocs` is an optional
extra for the SiliSocs adapter.

## Engine CLI

The package exposes `nuclear-war`.

```bash
uv run nuclear-war validate-rules
uv run nuclear-war simulate --mode table --players 3 --seed 42 --agent heuristic --max-turns 100 --out /tmp/sim.json
uv run nuclear-war simulate --mode postal --players 3 --seed 1 --agent random --out /tmp/postal.json
uv run nuclear-war experiment --mode table --players 3 --seed-start 1 --runs 10 --agent random --out /tmp/batch.json
uv run nuclear-war replay /tmp/sim.json
uv run nuclear-war summarize /tmp/sim.json
uv run nuclear-war live-server --seed 42 --players 3 --controlled player_0
```

`live-server` is a local development API for the visualizer's Live view.

## Decision-point contract

The engine is a decision-point state machine. Every strategic choice is an
explicit agent decision; mandatory steps run without pausing.

- `pending_decision(state)` returns the current `Decision`, or `None` at a
  terminal state.
- `apply_decision(state, action)` applies the choice, then runs all mandatory
  steps until the next decision.
- `observe(state, agent_id)` returns a typed, hidden-information-safe view.

An agent is anything with `choose(observation, options) -> action`. Option lists
come pre-ordered by the reference policy, so `HeuristicAgent` picks `options[0]`
and reproduces the deterministic baseline without consuming RNG.

PettingZoo AEC (table) and Parallel (postal) environments, the CLI, and all
agents are interfaces around this engine. They do not resolve rules on their
own.

## Agents, press, and factions

Seat names are shared by configs, tests, and docs.

- Baselines: `random`, `heuristic`, `decision_heuristic`.
- No-press language model seats: `llm_scripted`, `llm_first_legal` (offline,
  returns the first legal action from the rendered prompt), and `llm_http`
  (any OpenAI-compatible chat completions endpoint).
- Concordia seats: `concordia_scripted`, `concordia_first_legal`,
  `concordia_http`, and `concordia_native_*` variants that run the Concordia
  entity and log the model-visible prompt.
- `faction_c2`: one seat backed by several members whose votes map to a single
  legal action. Archetypes are `sole_authority`, `council`, `distributed`, and
  `automated`.

The press ladder has four modes: `none`, `press_light`, `multi_turn_public`,
and `full_press` (private single-recipient whispers plus structured
commitments). Press runs one game at a time through `concordia-demo`.

```bash
# No-press batch with offline seats
uv run nuclear-war llm-experiment --config docs/examples/no_press_llm_experiment.json --out-dir /tmp/llm_runs
uv run nuclear-war llm-summarize /tmp/llm_runs/summary.json

# Faction C2 batch
uv run nuclear-war llm-experiment --config docs/examples/faction_c2_experiment.json --out-dir /tmp/c2_runs

# Full press, offline (no model provider needed)
uv run nuclear-war concordia-demo --config docs/examples/concordia_full_press_style_demo.json --out-dir /tmp/press
```

Each press rung has an offline `concordia_*_style_demo.json` config in
`docs/examples/`; no-press, press-light, and full press also have a
provider-backed `concordia_*_together_demo.json` config. Provider-backed runs read
`TOGETHER_API_KEY` and a model name from the environment variable named in the
config (`TOGETHER_MODEL` in the Concordia examples, `WOPR_LLM_MODEL` for the
`together` preset). `uv run nuclear-war llm-preflight --config <config>` makes
one cheap completion call to check the endpoint before a live run. See `docs/pilot_experiment_runbook.md` for live runs.

## Artifacts

Replay JSON is the game record and its schema is fixed. Everything the language
layer produces is written beside it:

- `seed-*.replay.json`: engine replay, checked by an independent validator.
- `seed-*.replay.traces.json`: decision traces (prompts, raw responses, parse
  results, retries, validation errors, selected actions).
- Press and C2 artifacts: Concordia speech, whispers, commitments, and faction
  deliberation records.
- `summary.json`: batch aggregate with a config snapshot.

With press disabled, replay JSON is byte-identical to a no-press run at the same
seed. A sample four-seat no-press language model run is checked in under
`docs/demo_runs/`.
The `wopr_visualizer/` workbench in the repository root loads all of these.

## Development

```bash
uv run --extra dev python -m pytest -o addopts="" -q
uv run --extra dev ruff check src tests
uv run --extra dev ruff format --check src tests
uv run --extra dev pyright
uv run nuclear-war validate-rules
uv run scripts/validate-phase
```

`-o addopts=""` overrides the default `--maxfail=1`. Use `python -m pytest`
rather than a bare `pytest` so the project root is on `sys.path`. The only
expected skips are live-endpoint smoke tests that need model environment
variables. Set `WOPR_REQUIRE_CONCORDIA=1` to turn a missing Concordia install
into a failure instead of a skip.

`scripts/validate-phase` is the full gate: a 150-line limit for files under
`src/`, lint, format, type checks, tests, and API docs. The replay
parity sweep (3 and 4 players, `heuristic` and `random`, seeds 1-60) runs with:

```bash
uv run python scripts/run_parity_sweep.py
```

## Rules fidelity and sources

`docs/rule_fidelity_matrix.md` tracks which rules are implemented and verified.
The active variant is `base_later_two_d10`; other editions are deferred and
rejected at config time.

Card data in `rules/nuclear_war_base_cards.jsonl` holds names, counts, and
paraphrased effect summaries with confidence labels. It is not the published
card text, and the effect metadata is a low-confidence summary. Exact card text
and expansion deck composition need a physical copy or publisher-authorized
source; `docs/source_research_policy.md` and `research/source_evidence/`
describe how such evidence is recorded. The imported research bundle under
`research/imports/` holds source notes and the source index used by
`validate-rules`. Rulebook PDFs are not redistributed.

## Documentation

- `NUCLEAR_WAR_METHODOLOGY.md`: v1 scope and source model.
- `docs/specs/`: design specs for the decision interface, the Concordia harness
  and press ladder, faction C2, postal equipment, and the replay workbench.
- `docs/v1_acceptance.md`, `docs/variant_acceptance.md`: acceptance criteria.
- `docs/concordia_capability_map.md`: what the Concordia integration uses.
