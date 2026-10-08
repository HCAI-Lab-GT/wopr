# WOPR Visualizer

A replay debugger for the Nuclear War simulation engine. I built this to inspect
engine replay JSON and LLM decision-trace sidecars after a run. It also has a
local Live shell for one development session backed by the Python engine.

## What it does

The workbench loads engine replay JSON, optional decision-trace sidecars,
optional press artifacts, and optional failure snapshots. It reconstructs the
game state event by event. I can scrub through events, inspect the table, read
decision traces, review press messages, inspect failure context, and compare
batch runs.

### Replay view

The default view. It uses a table-first layout plus timeline.

- **Game table** reconstructs each player's table area from the events array:
  population, alive/eliminated state, war/peace state, hand count, secrets,
  deterrents, face-up card, queue slots, and per-event deltas. The active player
  and changed players get distinct treatment.
- **Context drawer** reads the selected replay context. Game mode has Event,
  Agent, and Conversation buttons. Forensic mode keeps exact event, action,
  trace, prompt, response, failure, and payload data available for audit.
- **Timeline** has filters (All / Combat / Population / Warnings), a play/pause
  button, prev/next, a range slider, a search box, and a marker rail for event,
  decision, press, launch, detonation, elimination, warning, and failure state.
- **Population chart** plots per-player population over turns as an inline SVG.
  It highlights the currently selected turn.

### Batch view

Loads a `summary.json` written by `nuclear-war llm-experiment` (see the
`nuclear_war` package). The whole output directory must be selected so the runs
can be resolved. It shows aggregate outcomes and lets me drill into a single run.

- **Batch summary** renders stat tiles (average turns, eliminations, decision
  traces, invalid actions, retries, provider totals) and tables for agent
  win/loss/draw, agent decision metrics, winner counts, and termination reasons.
- **Runs** lists every result (seed, winner, turns, termination, counts, replay
  filename). Click a resolvable row to load that run's replay and traces into
  the replay workbench and switch views.

Provider latency/cost rows show "no provider data" when the batch was produced by
heuristic agents that do not call an LLM.

### Live view

The Live view connects to a local `nuclear-war live-server` process. The Python
process owns the rules, state changes, stale-state checks, and replay export.
The browser reads the current table state and submits selected legal action IDs.
It does not run game rules.

Start the local API from the `nuclear_war` package:

```bash
nuclear-war live-server --seed 42 --players 3 --controlled player_0
```

When running from this repository without an installed console script, use:

```bash
cd ../nuclear_war
uv run nuclear-war live-server --seed 42 --players 3 --controlled player_0
```

Then start Vite, switch to **Live**, and set the **Live API URL** field to the
server URL, for example `http://127.0.0.1:8765`. Keep this local-only. The API is
intended for development on the same machine, not remote play or hosted sessions.

The browser action buttons submit the exact `action_id` values advertised by
`GET /decision`. Current replay artifacts are available from `GET /artifacts`
and can be loaded back into the replay workbench.

## Loading data

The toolbar has several entry points.

- **Sample replay** reloads the bundled single replay.
- **Sample batch** loads a bundled 3-run batch so the batch view has demo data.
- **Load replay** opens any engine replay JSON file.
- **Load traces** opens a decision-trace sidecar for the currently loaded replay.
- **Load press** opens a press artifact for the currently loaded replay.
- **Load failure** opens a decision-failure snapshot for audit.
- **Load batch directory** selects a `nuclear-war llm-experiment` output directory. The
  picker reads `webkitdirectory`, so I select the folder once and every
  `seed-*.replay.json`, `seed-*.replay.traces.json`, and `summary.json` is
  indexed. A Replay/Batch toggle appears once a batch is loaded.

The bundled batch fixtures under `src/data/` were produced by running
`nuclear-war llm-experiment` with mixed heuristic seats. They are real,
schema-accurate artifacts, kept in the repo so the Sample batch button and the
unit tests have deterministic data.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `←` / `→` | step one event back or forward |
| `Home` / `End` | jump to the first or last frame |
| `Space` | toggle play/pause auto-advance |
| `/` | focus the search box |

Search filters events by type, player id, and payload values. Prev/next search
match buttons step through matches, and the marker rail outlines matching frames.

## Project layout

Component files are colocated: `Component.jsx`, `Component.module.css`, and
`Component.test.jsx` live together. Pure replay logic is isolated in
`src/replay/` as plain modules with their own Vitest tests, separate from
rendering.

- `src/App.jsx` holds app state and routes between the replay and batch views.
- `src/components/ReplayView.jsx` composes the game table, context drawer,
  chart, and Timeline for a single replay.
- `src/components/BatchView.jsx` composes the Batch summary and Runs table.
- `src/replay/replayReducer.js` builds frames and infers initial state.
- `src/replay/batchSummary.js` and `batchValidation.js` read and validate batch
  `summary.json` payloads.
- `src/replay/populationSeries.js` derives the per-turn population chart data.
- `src/replay/searchMatches.js` handles event search and match navigation.
- `src/hooks/useReplayPlayback.js` owns keyboard scrubbing and auto-advance.

## Scripts

```bash
npm run dev        # start the Vite dev server
npm run build      # production build to dist/
npm run test       # run the Vitest unit suite
npm run lint       # run ESLint
npm run test:smoke # Playwright smoke test (starts its own dev server)
npm run test:smoke:live # Playwright live smoke test (starts local API and Vite)
```

## Paper figures

`npm run capture:appendix` regenerates the paper's appendix demo screenshots
under `output/playwright/appendix-demo/`. It starts its own Vite server and a
local `nuclear-war live-server`, so it needs `uv` and the `nuclear_war` package.
To also copy the images into a LaTeX checkout's `figures/demo/` directory, set:

```bash
WOPR_OVERLEAF_DIR=/path/to/paper npm run capture:appendix
```

## Screenshots

- `screenshot.png` shows the replay view with the sample replay loaded.
- `screenshot_batch.png` shows the batch view with the sample batch loaded.
