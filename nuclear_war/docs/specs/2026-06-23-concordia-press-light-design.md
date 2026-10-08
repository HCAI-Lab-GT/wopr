# Concordia Press-Light Design

Date: 2026-06-23

## Goal

Add press-light to the existing no-press Concordia harness so four AI-only
Concordia-backed seats complete one WOPR table game where, each completed round,
every living agent gets one public communication opportunity before the next
round's mechanical action selection.

WOPR remains the only rules engine and the source of legal actions. Concordia
supplies agent identity, memory/context framing, and action selection, and now
also supplies public statements. Public statements are recorded in sidecar
artifacts and injected into Concordia memory so they shape later decisions, but
they never mutate WOPR game state.

The design carries forward-looking seams toward multi-turn public press and full
press where they cost little now, and explicitly avoids speculative schema fields
and code paths that belong to those later rungs.

## Decisions

These decisions were made during planning:

1. Press-light fires once per round, not once per player turn. All living players
   speak once at the round boundary, after the per-round termination check and
   before the next round's decisions begin.
2. A reusable `PressCoordinator` abstraction owns the press pass now, structured
   so multi-turn public press extends it by looping the pass instead of
   rewriting it.
3. Strict failure behavior applies to press: a press message call that fails
   (bad model output, missing message, provider error) writes a failure snapshot,
   raises `ConcordiaRunFailure`, and stops the run. This matches the existing
   decision failure behavior.
4. Deterministic offline clients (`concordia_first_legal`, `concordia_scripted`)
   emit `decline` under press-light, so offline runs remain deterministic and
   never fake conversations. Real messages come only from `concordia_http` and
   `concordia_native_http` seats.
5. Press traces reach the visualizer through a separate sidecar,
   `concordia/press_traces.json`, loaded via a dedicated `Load press` control and
   auto-detected on demo-folder import.
6. Each press message record carries full trace parity with decision traces
   (prompt, raw responses, parse result, validation errors, retries, provider
   metadata), plus press-specific fields.

## Scope

In scope:

- One public communication opportunity per round for every living agent.
- `concordia/press_traces.json` sidecar with a press-light schema.
- Press messages injected into Concordia memory/context so later decision scenes
  see prior public statements.
- Strict press failure handling and a press failure snapshot path.
- Reusable `PressCoordinator` with a single public method for the press pass.
- Replay workbench `Load press` path, Conversation tab rendering, Forensic raw
  press JSON, and timeline press markers.
- Forward-looking schema seams (`audience`, `visibility`, `pass`, `press_mode`)
  that full press will populate, at no behavioral cost today.

Out of scope:

- WOPR replay schema changes.
- Any new WOPR `ActionType`, `EngineEvent`, or entry in `replay["actions"]`.
- Multi-turn press passes (more than one pass per round).
- Private channels, commitments, threats, promises, or later violation analysis.
- Any rule-level consequence of speech. Speech never mutates game state.
- Human play.
- Batch runner changes. `llm-experiment` stays no-press; press-light is
  single-game `concordia-demo` only for this milestone.
- Faked conversations or hidden chain-of-thought. Decline clients record a real
  `decline`; they do not invent statements.

## Architecture

The press layer is added to the existing `nuclear_war_concordia/` package,
following its split-module style. No new top-level package is created. The only
contact with the WOPR engine is a single optional `press_hook` callback in
`simulation.py`, which is additive and defaults to `None` so the no-press path
is byte-identical.

The dependency direction stays concordia -> wopr, never reversed. WOPR never
imports anything from `nuclear_war_concordia`.

### Layers

WOPR Engine Layer is unchanged. `pending_decision`, `observe`, and
`apply_decision` keep their contracts. Replay JSON, legal actions,
randomization, state mutation, replay events, and terminal outcomes stay WOPR
owned.

The round-boundary branch in `run_table_simulation_with_decision_agents`
(`simulation.py`) gains an optional `press_hook` callback. When set, the loop
calls it once per round after the termination check, passing `state` and the
completed round number, before calling `resume_round`. When `None`, behavior is
unchanged and parity is preserved.

Concordia Adapter Layer gains press scene rendering. The adapter renders a press
scene for a speaker from their WOPR `observe()` output, their identity, the list
of prior public messages visible to them, and the press legal options (`speak`
or `decline`). It parses Concordia output into either a message text plus an
optional rationale or an explicit decline.

Concordia Agent Layer keeps the same four AI-only agents. Under press-light,
each living agent produces one public message per round in addition to its
mechanical action choices. Deterministic offline clients emit `decline`; HTTP
and native clients produce real messages.

Press Coordinator Layer owns one press pass per round. It iterates living
speakers in turn order, renders each speaker's press scene, calls the Concordia
client, parses and validates the message, records a full-parity press trace, and
collects the round's public messages into a press log. That log feeds back into
each agent's memory so the next round's decision scenes and later speakers in
the same pass see prior statements.

Trace And Inspection Layer adds `concordia/press_traces.json`. Replay JSON stays
WOPR owned and unchanged. Decision traces in `wopr/traces.json` stay unchanged.
The replay workbench loads the press sidecar separately and renders it in the
Conversation tab and Forensic mode.

### Data flow

Each press-light round:

1. The table loop completes a full round and reaches `at_round_boundary`.
2. The loop checks termination as it does today. If the game continues, before
   `resume_round` it calls `press_hook(state, round_no)` when configured.
3. The `PressCoordinator` iterates living speakers in clockwise turn order.
4. For each speaker, it renders a press scene from the speaker's observation,
   identity, and the public messages visible so far (earlier rounds and earlier
   speakers this round).
5. The speaker's Concordia client produces one response.
6. The adapter parses the response into a message or a decline and validates it.
7. A full-parity press trace is appended to the press sink.
8. On validation failure, provider error, or missing message, the coordinator
   raises `ConcordiaDecisionFailure`, the harness wraps it as
   `ConcordiaRunFailure`, and `concordia/failure_snapshot.json` is written.
9. The coordinator returns the round's press log to the harness, which attaches
   it to each agent's press memory.
10. The loop resumes the next round. Mechanical action selection proceeds as
    today, with prior public statements now present in each decision scene.

### Memory injection

Each `ConcordiaDecisionAgent` holds an optional `press_memory` list of public
messages it has seen. `render_concordia_scene` includes that list in the scene
payload when present, so a player's decision scene reflects prior public
statements. Empty or absent `press_memory` reproduces the no-press scene
exactly. This is the forward-looking seam: multi-turn and full press extend what
populates this memory and how it is filtered per audience.

## Artifacts

### `concordia/press_traces.json`

A separate sidecar, validated against the replay reference exactly like
`wopr/traces.json`. The wrapper mirrors the decision-trace artifact shape:

```json
{
  "schema_version": 1,
  "press_mode": "press_light",
  "replay": {
    "mode": "table",
    "seed": 81,
    "agent": "decision_heuristic",
    "players": 4,
    "turns": 5
  },
  "messages": []
}
```

- `schema_version` is `1`. Future press modes can advance the schema without
  breaking older press-light artifacts.
- `press_mode` is the forward-looking seam. It is `press_light` today. Future
  values are `multi_turn_public` and `full_press`. The validator branches on it,
  so adding modes is additive.
- `replay` is the same reference object `wopr/traces.json` uses, so press and
  decision traces are tied to the same replay identity.

### Press message record

Each message record carries full trace parity with decision traces, plus
press-specific fields. Fields shared with decision traces keep identical names
and types. Press messages do not carry `selected_action_id` and are not
validated against `replay["actions"]`, because they are not game actions.

```json
{
  "message_id": "press:2:player_0:1",
  "turn": 2,
  "round": 2,
  "speaker": "player_0",
  "audience": "public",
  "visibility": "public",
  "pass": 1,
  "decision_type": "press",
  "rendered_observation": {},
  "prior_messages": [],
  "prompt": "",
  "prompts": [],
  "legal_options": [
    {"action_id": "speak", "label": "Speak"},
    {"action_id": "decline", "label": "Decline to speak"}
  ],
  "raw_response": "",
  "raw_responses": [],
  "parse_result": {"message": "", "rationale": ""},
  "text": "",
  "retries": 0,
  "validation_errors": [],
  "stated_rationale": "",
  "provider_latency_ms": null,
  "provider_cost": null,
  "provider_usage": null,
  "provider_label": null,
  "provider_model": null,
  "linked_decision_traces": []
}
```

Forward-looking fields, fixed at press-light values today:

- `audience` and `visibility` are always `public` in press-light. Full press will
  make `audience` a specific player id and `visibility` either `public` or
  `private`.
- `pass` is always `1`. Multi-turn public press will increment it within a round.
  The validator treats `pass` as a positive integer.
- `legal_options` is a list, matching decision traces. Press-light offers
  `speak` and `decline`. Full press can extend the option set.
- `linked_decision_traces` is an empty array in press-light. It is the hook for
  commitment and later violation analysis in full press. Validated as a list.

Fields deliberately not added to avoid speculation: `channel`, `recipient_set`,
`commitment_target`, `violation_status`. These belong to the full-press design.

### Linking press to WOPR decisions

Press messages do not carry WOPR action ids and are not validated against
`replay["actions"]`. Linking is one-directional and by identity: each message
carries `turn`, `round`, and `speaker`. The visualizer joins press messages to
decision traces by `turn` and `player_id` for display only. No replay schema
change and no replay action validation.

### Failure snapshot reuse

Press failures reuse the existing `failure.py` path. A new `press_failure()`
builder, sibling to `decision_failure()`, writes the same snapshot fields plus
`pass` and `audience`. `ConcordiaRunFailure` propagates it to
`concordia/failure_snapshot.json`. No new top-level failure type is introduced.

### Config additions

`ConcordiaNoPressConfig` gains an optional `press` block parsed with strict field
validation in the existing style:

```json
{
  "players": 4,
  "seed": 81,
  "max_turns": 50,
  "runtime": "auto",
  "press": {"mode": "press_light", "enabled": true},
  "seats": {}
}
```

`press.mode` is one of `{"none", "press_light"}`. `none` is the default and
reproduces the no-press harness exactly. `press_light` activates the
coordinator. Adding `multi_turn_public` or `full_press` later is one set entry
plus a coordinator branch. The config stays a single dataclass family; it is not
forked into a separate `PressConfig` hierarchy.

## Code Layout

New files in `nuclear_war/src/nuclear_war_concordia/`:

- `press_scene.py` renders a press scene for a speaker: their WOPR observation,
  identity, prior public messages visible to them, and the press legal options.
  Mirrors `scene.py`.
- `press_response.py` parses press model output into a message text plus an
  optional rationale, or a decline. Mirrors `response.py`.
- `press_trace.py` builds a full-parity press message record and appends to the
  press sink. Mirrors `trace.py`. No `selected_action_id`. Shares the
  provider-metadata helper that wraps the existing `llm_completion` calls.
- `press_coordinator.py` is the `PressCoordinator`. Owns one press pass per
  round. One public method today, `run_round_press(state, config, round_no)`.
  Structured so multi-turn press wraps an internal `run_pass()` in a loop later.
- `press_artifacts.py` builds and validates `concordia/press_traces.json`.
  Sibling to `llm_trace_artifacts.py`, reusing the shared provider-metadata
  helper that wraps the existing `llm_completion` calls.
- `press_config.py` parses the `press` config block with strict field validation.

Modified files:

- `config.py` adds an optional `press: PressConfig` defaulting to `mode="none"`.
- `config_constants.py` adds `PRESS_MODES = {"none", "press_light"}`.
- `simulation.py` adds the optional `press_hook` callback to the round-boundary
  branch. Defaults to `None`.
- `harness.py` invokes the coordinator when `config.press.mode == "press_light"`.
- `harness_agents.py` wires press behavior per seat type (decline for offline
  clients, real messages for HTTP/native).
- `agent.py` adds optional `press_memory` to `ConcordiaDecisionAgent`.
- `scene.py` includes `press_memory` in the decision scene payload when present.
- `failure.py` adds the `press_failure()` builder.
- `artifacts.py` writes `concordia/press_traces.json` when press ran.
- `harness_payloads.py` adds press counts to `run_summary.json`.
- `llm_harness_cli.py` runs press when the config requests it. No new command.

Each new module stays under 150 lines by reusing the existing split style.
WOPR's `decision_loop.py` internals stay untouched; the only engine contact is
the `press_hook` callback in `simulation.py`.

## Visualizer

`wopr_visualizer` gains a separate press sidecar path. The current code reads a
`press` field from `traceArtifact` (`App.jsx`); this design migrates that to a
dedicated press source.

- `src/replay/pressArtifacts.js` provides `parsePressArtifactJson(text, replay)`
  and `normalizePressArtifacts(payload)`. The latter returns the `{ messages,
  source }` shape `conversationArtifacts.js` already consumes.
- `App.jsx` adds `pressArtifact` state and computes `conversationArtifacts` from
  it instead of from `traceArtifact`.
- `ImportBar.jsx` adds a `Load press` control matching the `Load traces` and
  `Load failure` pattern.
- Demo-folder import auto-detects `concordia/press_traces.json`.
- `ConversationPanel.jsx` renders messages from `conversationArtifacts` and shows
  the forward-looking `audience` and `visibility` fields.
- `ForensicPanel.jsx` adds a press-traces raw JSON section for audit.
- `timelineMarkers.js` continues to join press messages by turn; only the data
  source changes.

Web guidelines are respected: styles extracted to CSS modules, handlers moved to
named functions, configs declared as constants outside components, components
colocated, and an error boundary on the file parse.

## Error Handling

Press-light keeps strict development behavior.

Strict failures:

- Press scene rendering failure.
- Failure to parse a non-decline message when one was required.
- Provider error, timeout, or HTTP error during a press call.
- Trace schema validation failure.
- Replay/press identity mismatch.

Recoverable once:

- Malformed press model output.
- Empty message text.
- A response that is neither a valid message nor a valid decline.

For recoverable cases, retry once with validation feedback. If retry fails, the
run fails by default in development mode. A configured fallback action is not
enabled for press-light development runs.

Failure snapshot behavior mirrors the decision path. A press failure raises
`ConcordiaDecisionFailure`, the harness wraps it as `ConcordiaRunFailure`, and
`concordia/failure_snapshot.json` is written with the press scene, raw visible
responses, parse result, validation errors, provider metadata, and sanitized
exception details. Press failure snapshots also record `pass` and `audience`.

## Testing And Verification

Python tests, table-driven and seeded, following `test_concordia_no_press_harness.py`:

- `test_press_config.py` accepts `press.mode=press_light`; rejects unknown modes,
  non-bool `enabled`, and extra fields; `none` default reproduces no-press.
- `test_press_scene.py` renders speaker observation, identity, prior messages,
  and speak/decline options.
- `test_press_response.py` parses `{"message", "rationale"}` and
  `{"action_id":"decline"}`; rejects malformed input.
- `test_press_trace.py` builds a full-parity record with no `selected_action_id`
  and reuses the shared provider-metadata helper.
- `test_press_coordinator.py` runs one pass per round over living speakers,
  skips dead players, records decline clients as decline, and injects prior
  messages into the next speaker's scene within the same pass.
- `test_press_artifacts.py` validates the sidecar against the replay reference
  and rejects unknown fields, bad schema versions, and message/replay mismatches.
- `test_press_harness.py` integration: four first-legal agents complete a
  press-light game, `press_traces.json` is written, replay is unchanged, and one
  scripted failure raises `ConcordiaRunFailure` and writes `failure_snapshot.json`.
- Parity gate: press-light with `mode=none` produces byte-identical replay to the
  existing no-press harness, asserting the `press_hook` default-`None` path.

JavaScript tests, following existing helper and panel test style:

- `pressArtifacts.test.js` covers parse and normalize, including absent data
  returning `{messages:[], source:'none'}`.
- `ConversationPanel.test.jsx` renders public messages with turn, speaker, and
  audience.
- `App.test.jsx` wires the `Load press` control, preserves the no-press empty
  state, and keeps raw JSON in Forensic only.

Smoke test loads a Concordia press demo folder and checks the Conversation tab,
Forensic raw press JSON, and timeline press markers.

Env-gated live smoke: one `concordia_http` or `concordia_native_http` press-light
game completes with real messages. Skipped without provider environment.

### Native runtime open verification point

The no-press native path used the `choice` and `act` action spec on discrete
options. Press-light requires free-text message production from the native
Concordia entity. Whether the native entity produces well-formed free-text
messages through a `sample_text`-style action spec has not been verified against
the installed runtime. This is treated as an open verification point, not a
solved design. The live smoke step tests it empirically. If the native entity's
free-text path is unreliable, press-light falls back to the HTTP model for
message production while keeping the native runtime for action selection, and
this is recorded in run metadata.

## Press Mode Ladder

This design implements the press-light rung. The ladder is preserved for
context.

### No-Press

Agents only choose legal WOPR actions. No communication.

### Press-Light

This design. Each living agent gets one public communication opportunity per
round. Messages are public, trace-only, injected into Concordia memory, and do
not mutate WOPR state.

### Multi-Turn Public Press

Agents participate in multiple public communication passes before mechanical
action selection. The `PressCoordinator.run_pass()` seam and the `pass` field
support this. Not implemented here.

### Full Press

Public and private channels, multi-turn negotiation, commitments, threats,
promises, deception, and later violation analysis. The `audience`,
`visibility`, and `linked_decision_traces` seams support this. WOPR still owns
legal actions and resolution. Any rule-level consequence of speech needs a
separate explicit design. Not implemented here.
