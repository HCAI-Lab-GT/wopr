# Nuclear War V1 Acceptance

This page defines the evidence I need before treating Nuclear War v1 as ready
for experiments. It is a working acceptance target, not a release claim.

## Rule Fidelity

- Table mode uses the deterministic engine for draw, queue, target, launch,
  fallout, elimination, and termination behavior.
- Draw legality and draw resolution count hand, face-down, and deterrent cards
  toward the active hand draw target.
- War begins when a warhead target is declared, including attacks later blocked
  by sabotage, interception, dud, or misfire.
- Peace restoration after completed eliminations clears both the global peace
  flag and every player's war flag, and waits for pending final strikes.
- Postal mode uses the deterministic engine for complete seeded no-press games.
- Postal no-press mode disables player communication instead of adjudicating it.
- Public v1 runtime and replay paths, including setup helpers, reject postal
  press mode, press events, and malformed press flags instead of creating
  partially supported press-enabled or press-shaped state.
- Legal actions serve engine, CLI, agents, and env adapters.
- Postal legal actions cover propaganda, secrets, espionage, defense, sabotage,
  cruise, submarine, atomic/space setup/use, Supervirus, final-strike
  targeting, and peace votes.
- Player observations do not expose hidden hands, face-down cards, or private
  postal orders from other players.
- `docs/rule_fidelity_matrix.md` records implemented base-card behavior and
  card families that are not verified by the active registry.
- `docs/source_research_policy.md` records how imported source bundles affect
  source priority, edition boundaries, and exact-text limits.
- `docs/source_research_policy.md` records the 2026-06-14 bundle as the current
  project import and distinguishes source-index IDs from legacy local source
  labels.
- Rule validation reports restricted exact-text fields and v1 requires that
  list to be empty for the active registry.
- Rule validation reports unresolved source labels and v1 requires that list to
  be empty for the active registry.
- Rule validation reports the number of source IDs loaded from the imported
  `source_index.json`.
- Rule validation reports malformed JSONL, IDs/names/types, duplicate IDs,
  missing source evidence, invalid deck counts, or invalid confidence fields.
- Active card and rule records have source evidence and confidence fields where
  behavior depends on unofficial or edition-sensitive material.
- Legacy source labels in the active registry are mapped to imported
  source-index IDs or documented as unresolved traceability gaps.

## Runtime Interfaces

- `nuclear-war validate-rules` checks the registry-backed rules data.
- Rule validation reports unsupported effect keys from the active registry.
- Rule validation reports missing postal special metadata and metadata records
  counted into the base deck.
- Rule validation reports the active edition variant instead of relying on
  implicit setup assumptions.
- Rule validation reports the known variant catalog, and runtime configs reject
  deferred variants before alternate edition behavior can run.
- `docs/variant_acceptance.md` records per-edition acceptance criteria for
  active and deferred variants.
- Runtime setup and simulation result metadata resolve the requested active
  variant instead of relying on hard-coded active globals.
- Rule validation reports informational source blockers for remaining physical-copy
  and authorized-source gates without treating them as validation failures.
- Rule validation reports source-linked rules-trace scaffold records and source-mapped
  rule-step records for current table replay action/event families.
- Rule validation reports a bounded full-game semantic rules-trace summary for a
  deterministic table replay and no full-game trace gaps.
- `nuclear-war simulate` writes bounded replay-safe JSON for one seeded game,
  including active variant metadata.
- `nuclear-war simulate --variant` accepts the active variant and rejects deferred
  variants before any alternate edition behavior can run.
- `nuclear-war simulate --agent decision_heuristic` accepts table mode and rejects
  postal mode until postal observations are typed.
- Stochastic fallout events in replay logs include the active randomizer and
  source table id.
- All stochastic attack events that use the fallout/randomizer table include
  raw result, effect, multiplier, target adjustment, active randomizer, and
  source table id.
- `nuclear-war experiment` writes compact JSON for seeded baseline batches,
  including active variant metadata in each result row.
- `nuclear-war experiment --variant` accepts the active variant and rejects
  deferred variants before any batch simulation starts.
- `nuclear-war experiment --agent decision_heuristic` accepts table mode and
  rejects postal mode until postal observations are typed.
- `nuclear-war replay` prints a stored JSON log.
- `nuclear-war summarize` prints the replay summary fields.
- Replay commands reject missing, non-file, malformed, or schema-incomplete
  replay JSON with a nonzero code and clear error.
- Replay commands reject valid JSON that is not an object with a nonzero code
  and clear error.
- Replay JSON must include nonempty action and event logs, not only summary
  fields.
- Replay validation checks required fields in each single-game action log entry.
- Replay validation checks required fields in each single-game event log entry.
- Replay validation rejects malformed single-game action or event entry field
  types, unknown player ids, and inconsistent action ids in logs.
- Replay event log entries include the turn that produced the event.
- Replay validation rejects action or event log turns outside the stored game
  turn range.
- Replay validation rejects action or event logs whose turn sequence moves
  backward.
- Replay validation rejects single-game logs with invalid or non-string mode or
  agent values, malformed seed, missing decisive winner, invalid cutoff winner
  claims, contradicted population or termination reason data, or active variant.
- Replay and experiment validation reject boolean values in numeric schema
  fields, including batch summary counts.
- Experiment batch JSON remains readable through `nuclear-war replay` with its
  own compact batch schema.
- Experiment batch replay validation checks required fields in each compact
  result row.
- Experiment batch replay validation rejects compact result rows with malformed
  variant, winner, elimination, final-population, or termination-reason data.
- Experiment batch replay validation rejects malformed batch metadata and
  result counts that do not match the declared `runs` value.
- Experiment batch replay validation rejects result rows whose mode, agent,
  seed order, or turn count contradicts the batch header.
- Experiment batch replay validation checks required batch summary fields.
- Experiment batch replay validation rejects summaries whose termination counts,
  winner counts, average turns, or elimination totals contradict result rows.
- Experiment batch JSON is summarizable through `nuclear-war summarize` using
  its stored batch summary.
- CLI command validation returns a nonzero code with a clear error instead of
  surfacing Python exceptions for invalid v1 configuration.
- CLI parser-level invalid choices return a nonzero code when invoked through
  `main([...])` instead of raising `SystemExit`.
- Runtime helpers reject unknown mode strings before creating game state or
  replay logs.
- Runtime helpers reject games with fewer than two players before creating game
  state or replay logs.
- Runtime helpers reject malformed non-integer player counts and seeds before
  creating game state or environments.
- Runtime helpers reject non-positive turn limits before creating replay logs.
- Runtime simulation and experiment configs reject boolean numeric values before
  creating game state or starting batch simulations.
- Runtime simulation and experiment configs reject malformed non-string mode and
  agent values with controlled errors.
- Simulation rejects invalid mode, player count, turn limit, agent type, and
  press mode before loading rule data or creating game state.
- `create_table_env` exposes table play as a PettingZoo AEC environment and terminates eliminated non-retaliating players.
- `create_postal_env` exposes postal no-press play as a PettingZoo Parallel
  environment.

## Experiments

- Random and heuristic agents choose only legal actions.
- The table-only `decision_heuristic` agent chooses from typed observations and
  replay-valid legal options.
- Seeded runs are reproducible.
- Batch output records seed, mode, agent type, winner, turns, eliminations,
  final populations, and termination reason.
- Batch summaries report termination counts, winner counts, average turns, and
  total eliminations.

## Guardrails

- `ruff check` must pass.
- `ruff format --check` must pass.
- `pyright` must pass.
- `pytest` must pass.
- `scripts/validate-phase` must pass.
- Benchmark output remains required, but optimization is not a v1 acceptance
  criterion unless a measured bottleneck appears.
- Benchmark output includes table and postal no-press simulation metrics.

## Source Evidence

- `docs/v1_source_evidence.md` records the imported research-bundle acceptance
  requirements and source-boundary constraints.
- `nuclear-war validate-source-evidence` checks explicit draft source-evidence
  paths before promotion into live manifest names.
- Source-evidence coverage payloads such as `card_effect_evidence_coverage`
  and `expansion_composition_evidence_coverage` report missing, recorded,
  verified, and unverified target IDs as capture progress only.
- Live source-evidence manifests must contain only second-pass verified records.
  Draft or otherwise unverified live records produce promotion errors such as
  `card_effect_evidence_promotion_errors` before any source blocker can clear.

## Out Of Scope

- Press adjudication, language-model agents, external social-simulation frameworks,
  web interfaces, and tournament ratings are deferred.
