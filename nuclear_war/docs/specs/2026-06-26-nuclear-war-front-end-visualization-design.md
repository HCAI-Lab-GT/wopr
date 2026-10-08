# Nuclear War Front-End Visualization: Design Spec

- **Date:** 2026-06-26
- **Scope:** Phased front-end visualization and live browser decision shell
- **Primary package:** `wopr_visualizer`
- **Engine package:** `nuclear_war`
- **Selected approach:** shared table substrate first

## 1. Goal

I want the Nuclear War browser surface to read as a game table first, not as a
raw replay debugger. Phase 1 improves the existing replay workbench by making
the reconstructed table state the primary reading surface. Phase 2 adds a thin
local browser shell for live decision control without moving rules into the
browser.

The common design rule is that replay mode and live mode normalize their data
into the same table view model. The board components should not need to know
whether the state came from replay JSON or from a live local API.

## 2. Decisions

- Build both replay visualization and live controls in phases.
- Phase 1 uses a Table First layout.
- The board becomes a card-table reconstruction, not only compact player
  strips and not a tactical map abstraction.
- Phase 2 uses a thin local Python API.
- Phase 2 serves a hybrid operator: human legal-action selection plus research
  override and inspection workflows.
- Python remains the rules source of truth.
- The browser renders state, displays evidence, and submits legal action IDs.

## 3. Scope

### Phase 1: replay workbench

In scope:

- A reusable table component stack for the current replay workbench.
- A normalized table view model built from replay frames.
- Player table areas with population, status, hand count, secrets,
  deterrents, face-up card, queue slots, and deltas.
- Selected context linking table state to event story, related action, agent
  trace, press messages, forensic JSON, and warnings.
- Existing replay, trace, press, failure snapshot, and batch validation
  preserved.
- Desktop and 390px mobile visual QA.

Out of scope:

- Live play.
- New replay schema fields.
- Python engine changes.
- Canvas, WebGL, Phaser, Three.js, or 3D scene work.

### Phase 2: live browser shell

In scope:

- A small local Python API over the existing decision-machine contract.
- Browser controls for the pending decision and legal actions.
- Human action submission for controlled seats.
- Agent-step control for research operation.
- Structured API errors for invalid or stale submissions.
- Export of replay and trace artifacts for review in the workbench.

Out of scope:

- Browser-side rule execution.
- Browser-generated action payload semantics beyond selecting legal action IDs.
- Remote multiplayer.
- Hosted production service.
- Replacing existing CLI experiment flows.

## 4. Architecture

The shared architecture has two source adapters and one table model.

Phase 1 source path:

```text
Replay JSON + trace sidecar + press artifact
  -> existing replay reducers and artifact parsers
  -> ReplayTableAdapter
  -> TableViewModel
  -> GameTable components
```

Phase 2 source path:

```text
Local Python API
  -> LiveTableAdapter
  -> TableViewModel
  -> GameTable components
```

The browser does not duplicate game rules. Python owns:

- player state,
- hidden-information views,
- pending decisions,
- legal actions,
- action application,
- replay and trace artifact writing.

The browser owns:

- table presentation,
- selected context,
- local UI state,
- import and API error presentation,
- choosing a legal action ID to submit.

## 5. Component Design

### `TableViewModel`

The table view model is the browser-facing shape shared by replay and live
mode. It should include:

- replay or live source metadata,
- players in stable display order,
- per-player population,
- alive or eliminated state,
- war or peace state,
- hand count,
- secret count,
- deterrent count,
- face-up card summary,
- two queue slots,
- per-player deltas,
- active player,
- selected table object,
- related event and action,
- related decision trace,
- related press messages,
- warnings and forensic payload links,
- Phase 2 pending decision and legal actions when present.

### `GameTable`

`GameTable` owns layout only. It receives a `TableViewModel`, selected context,
and callbacks. It renders the current event strip, the player table areas, and
the compact timeline region.

### `PlayerTableau`

`PlayerTableau` renders one player as a card-table area. It includes:

- population display,
- alive or eliminated state,
- war or peace state,
- hand count,
- secrets,
- deterrents,
- face-up card,
- queue lane,
- inline deltas,
- active and selected state treatment.

### `CardZone`

`CardZone` is a small reusable zone for counts or card summaries. It is used
for hand, secrets, deterrents, and face-up card display. It does not infer card
semantics.

### `QueueLane`

`QueueLane` renders the two queue slots. It shows empty slots, card IDs or
labels when present, selected-slot state, and movement deltas.

### `ContextDrawer`

`ContextDrawer` replaces a raw-data-first inspector. It reads the selected
table context and can show:

- event story,
- related replay action,
- linked agent decision trace,
- press messages for the selected turn or player,
- forensic JSON,
- warnings and validation errors,
- Phase 2 legal actions for the pending decision.

The drawer should not compete with the table by default. It is the secondary
surface attached to a selected object.

## 6. Layout

The default desktop layout:

- top import and status bar,
- current event strip above the board,
- main table area with player tableaus,
- right context drawer,
- compact timeline below the table.

The default mobile layout:

- top import and status bar,
- current event strip,
- stacked player tableaus,
- collapsible or below-board context drawer,
- compact timeline controls.

The table should remain the main reading surface. Agent, press, and forensic
evidence remain reachable without being equal-weight panels on first view.

## 7. Phase 2 Local API

The live shell API should be local-only and scoped to the engine contract.

### Endpoints

`GET /session`

- Returns session metadata: mode, seed, players, active variant, configured
  seats, and current run status.

`GET /state`

- Returns the current table state needed by the live table adapter.
- Includes public table state and the selected seat view when a seat is active.

`GET /decision`

- Returns the current pending decision, decision owner, decision type, legal
  actions, and observation-derived display context.
- Returns an empty pending decision when the game is terminal.

`POST /decision`

- Accepts one legal action ID for the current pending decision.
- Applies it through Python.
- Returns the new state, new pending decision, latest events, and any trace
  metadata produced by the action.

`POST /step-agent`

- Lets the configured agent choose for the pending decision.
- Returns the same response shape as `POST /decision`.

`GET /artifacts`

- Returns or writes available replay, trace, run metadata, warnings, and
  validation artifacts for review in the replay workbench.

### API rules

- Legal actions come from Python only.
- Browser submissions use legal action IDs.
- Hidden-information views come from Python observation data.
- Invalid action IDs return structured errors and do not mutate state.
- Stale decision submissions are rejected.
- API errors are visible in the context drawer and forensic view.

## 8. Error Handling

Phase 1 errors:

- invalid replay JSON,
- replay validation errors,
- mismatched trace sidecar,
- mismatched press artifact,
- unsupported reducer events,
- missing optional press data,
- failure snapshot validation errors.

These stay in the existing import and validation flow. Selected-context errors
also appear in the context drawer when tied to a table object or event.

Phase 2 errors:

- invalid action ID,
- stale decision ID,
- missing pending decision,
- seat mismatch,
- terminal game mutation attempt,
- local API failure,
- artifact export failure.

Mutation errors must fail closed. A failed action submission should not advance
the engine state.

## 9. Testing

Phase 1 tests:

- table view model helper tests for player state, card zones, queue slots,
  deltas, selected context, and evidence links,
- component tests for `GameTable`, `PlayerTableau`, `CardZone`, `QueueLane`,
  and `ContextDrawer`,
- regression tests for existing replay, trace, press, failure, and batch
  parsing behavior,
- smoke tests for sample replay, trace artifact, press artifact, desktop, and
  390px mobile.

Phase 2 tests:

- API tests for session, state, pending decision, action submission,
  agent-step, and artifact export,
- mutation tests proving invalid and stale submissions do not change state,
- hidden-information tests proving browser-visible seat data comes from Python
  observation data,
- export tests proving live sessions produce replay and trace artifacts that
  the workbench can load.

Phase 2 adds focused Python API tests and any engine tests touched by the live
session plumbing.

## 10. Risks

### Replay and live state may drift

The shared `TableViewModel` limits this risk. Phase 1 should build the model
from replay frames first. Phase 2 should add a live adapter that produces the
same shape.

### Context drawer can become another raw inspector

The drawer should default to readable selected-context summaries. Raw payloads
remain available under forensic sections.

### Live API scope can grow

The Phase 2 API should expose only the current engine contract: state,
observation, pending decision, legal actions, action application, agent-step,
and artifact export.
