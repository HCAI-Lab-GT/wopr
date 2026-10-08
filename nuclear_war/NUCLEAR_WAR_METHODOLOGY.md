# Nuclear War V1 Methodology

## Project State

I use `nuclear_war` as the first maintained game package in WOPR.

The v1 goal is a deterministic Nuclear War implementation that can run complete table and postal no-press games without language-model involvement. PettingZoo is an interface layer. The rules engine remains the source of game state and resolution.

## V1 Completion Criteria

- Table mode runs through a sequential AEC environment.
- Postal no-press mode runs through a Parallel environment.
- Legal actions are generated from the current game state.
- Observations are scoped to each player and do not leak hidden cards or private orders.
- The CLI can validate rules, simulate games, replay JSON logs, and summarize logs.
- Random and heuristic agents can run seeded experiments.
- Replay logs include active variant, seed, mode, agent type, actions, events, winner, final populations, and termination reason.
- Tests cover unit rules, complete seeded games, CLI behavior, PettingZoo compliance, and reproducibility.
- `docs/v1_acceptance.md` records the concrete evidence required before v1 is treated as experiment-ready.
- `docs/rule_fidelity_matrix.md` records implemented rule coverage and registry limits.

## Scope Boundaries

### In Scope For V1

- Registry-backed card loading.
- Deterministic table and postal no-press rules.
- Full non-communication postal phase ordering.
- Scriptable experiments with random and heuristic agents.
- Benchmarks that write JSON results and detect regressions.
- Documentation that states observed behavior and known limitations.
- Source provenance for imported rule and card research.

### Out Of Scope For V1

- Press adjudication.
- Language-model agents.
- External social-simulation frameworks.
- Web UI.
- Tournament ratings.

## Architecture

- `nuclear_war_env` owns rules, state, actions, observations, environments, and simulation.
- PettingZoo adapters call shared legality and observation functions.
- CLI commands call the same simulation and replay functions used by tests.
- Agents choose from legal actions only. They do not mutate state directly.
- Experiment output is replay data, not a second source of game truth.
- Imported research bundles live under `research/imports/` and inform specs.
  They are not imported directly into runtime state.
- The 2026-06-14 research bundle is the current project import. Its
  `source_index.csv` and `source_index.json` are the source-ID ledger for new
  provenance work.

## Source Model

I keep v1 as one explicit rule target instead of blending editions:

- Classic/base Nuclear War is the first table-play target.
- The active v1 variant is `base_later_two_d10`.
- Postal no-press is a controlled WOPR mode that removes communication while
  retaining non-communication postal mechanics.
- Current Nuclear Destruction rules are a related modern branch for future
  edition modules.
- Community card lists can guide names and counts, but exact card wording and
  disputed behavior require a physical copy or publisher authorized source.
- Source conflicts should become variant flags or documented rule-fidelity
  limits.
- Active registry source labels should resolve to imported source-index IDs.
  `nuclear-war validate-rules` loads those IDs from `source_index.json` and
  reports unresolved labels as a v1 gate.
- The imported simulation schema names additional edition-boundary fields:
  initial face-down cards, anti-missile turn jump, expansion sets, special
  powers, and trading. I expose fixed v1 values for those fields before adding
  more edition modules.

## Work Order

1. Update documentation.
2. Preserve raw research imports and record how each bundle affects v1 source
   boundaries.
3. Add failing tests for public v1 behavior.
4. Implement shared legal actions and observations.
5. Implement deterministic simulation and replay logs.
6. Add random and heuristic agents.
7. Replace Phase 0-only factories with real table and postal environment factories while keeping legacy stubs available.
8. Wire the CLI.
9. Extend benchmarks and validation.
10. Keep registry source labels reconciled to source-index IDs or document the gap.
11. Run `pyright`, `ruff check`, `ruff format --check`, `pytest`, and `scripts/validate-phase`.

## Known Limits

⚠️ The local rules sources need to remain the reference for unresolved card or postal details. When a rule cannot be represented with confidence, I document the gap and add a validation failure instead of silently inventing behavior.

⚠️ The imported research bundle confirms unresolved edition conflicts around
population deck size, randomizer model, hand target, and exact card text. V1
reports the active `base_later_two_d10` choice; alternate edition modules remain
specification inputs, not proof that v1 is complete.

⚠️ The current card registry resolves its source labels to imported source-index
IDs, but some effects remain low-confidence summaries. Source-ID reconciliation
does not replace physical-copy or authorized-source verification for exact text.

⚠️ The active runtime variant payload records fixed values from the imported
variant schema. Anti-missile turn-order jumps now have table-env and simulation
tests. Future variant fields that affect turn flow need the same kind of
behavior-level coverage.
