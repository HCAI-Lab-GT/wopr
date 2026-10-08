# Concordia Multi-Turn Public Press Design

Date: 2026-06-24

## Goal

Add multi-turn public press as a new press mode on top of press-light. Each
completed round, all living agents participate in a fixed number `N` of public
communication passes before the next round's mechanical action selection.
Within each pass every living agent speaks once, in clockwise (turn) order.
Between passes, each agent sees the full accumulating transcript of all public
messages produced so far in the round.
After `N` passes, action selection proceeds with the complete transcript in each
agent's memory.

WOPR remains the only rules engine and the source of legal actions. Press is
still public and trace-only. It never mutates WOPR game state, and the replay
JSON stays unchanged.

## Decisions

These decisions were made during planning:

1. The number of passes per round is fixed at a config value `passes`. Every
   living agent speaks once per pass for exactly `N` passes. `passes` is
   required in the config block when mode is `multi_turn_public`. No dynamic
   termination by vote or silence. Fixed N keeps cost bounded and makes
   seed-matched comparison across runs straightforward.
2. Each speaker sees the full transcript: every public message from earlier
   passes and from earlier speakers in the current pass. This lets agents
   respond to each other before committing to mechanical actions.
3. Multi-turn public press is a new distinct mode `multi_turn_public`, not a
   `passes` field added to `press_light`. Press-light behavior and its
   existing artifacts stay unchanged.
4. All messages remain `audience="public"` and `visibility="public"`. Private
   channels and addressed-to-a-player public messages are deferred to full
   press.

## Scope

In scope:

- A new `multi_turn_public` press mode with a fixed `passes` count per round.
- The press coordinator looping passes internally, threading the accumulating
  transcript as `prior_messages` into each speaker.
- The `pass` field on press message records ranging `1..N`.
- Config validation that `passes` is a positive integer, required when mode is
  `multi_turn_public`, and forbidden otherwise.
- A `multi_turn_public` example config and harness integration test.
- Visualizer verification that multi-turn artifacts render in the Conversation
  tab and pass through the existing smoke path.

Out of scope:

- WOPR replay schema changes.
- Any new WOPR `ActionType`, `EngineEvent`, or entry in `replay["actions"]`.
- Dynamic pass termination by vote or silence.
- Private channels, addressed-to messages, commitments, threats, promises, or
  violation analysis. Those are full press.
- Any rule-level consequence of speech. Speech never mutates game state.
- Human play.
- Batch runner changes. `multi_turn_public` is single-game `concordia-demo`
  only.
- Any change to press-light behavior or artifacts. Press-light is a distinct
  mode and stays at one pass.
- Native Concordia press message production. HTTP remains the press producer.

## Architecture

Multi-turn public press is a small extension of the press-light coordinator.
The seams reserved for it in the press-light design are now used: the `pass`
field on message records, the `pass_no` argument to `press_failure` and
`append_press_trace`, and the `multi_turn_public` entry already present in the
validator's accepted modes.

The dependency direction stays concordia -> wopr. The only engine contact
remains the single optional `press_hook` callback in `simulation.py`, which is
unchanged. WOPR never imports anything from `nuclear_war_concordia`.

### Data flow

Each multi-turn press round:

1. The table loop completes a full round and reaches `at_round_boundary`.
2. The loop checks termination as it does today. If the game continues, before
   `resume_round` it calls `press_hook(state, completed_round)` when configured.
3. The `PressCoordinator` runs `passes` communication passes. For each pass
   `p` in `1..N`:
   1. It iterates living speakers in clockwise turn order.
   2. For each speaker, it renders a press scene from the speaker's observation,
      identity, and the full transcript of all messages produced so far this
      round (earlier passes plus earlier speakers in the current pass).
   3. The speaker's Concordia client produces one response.
   4. The adapter parses the response into a message or a decline and validates
      it.
   5. A full-parity press trace is appended with `pass=p`.
   6. On validation failure, provider error, or missing message, the coordinator
      raises `ConcordiaDecisionFailure` with the actual `pass_no`, the harness
      wraps it as `ConcordiaRunFailure`, and `concordia/failure_snapshot.json`
      is written.
   7. The message is appended to the round's transcript, visible to later
      speakers in this pass and all speakers in later passes.
4. The coordinator returns the round's full transcript to the harness, which
   attaches it to each agent's `press_memory` exactly as press-light does.
5. The loop resumes the next round. Action selection proceeds with the complete
   transcript present in each decision scene.

### Memory injection

Memory injection works exactly as in press-light. Each `ConcordiaDecisionAgent`
holds a `press_memory` list of public messages it has seen. `render_concordia_scene`
includes that list in the scene payload when present. The only difference is
that the transcript multi-turn agents see is longer, because it spans multiple
passes. Empty or absent `press_memory` still reproduces the no-press scene.

## Artifacts

### `concordia/press_traces.json`

The sidecar wrapper is structurally identical to press-light. The only change
is that `press_mode` is `"multi_turn_public"` and `messages` contains records
across multiple passes per round.

```json
{
  "schema_version": 1,
  "press_mode": "multi_turn_public",
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

The validator (`press_artifacts.py`) already accepts `multi_turn_public` in its
`PRESS_MODES` set. No validator change is needed for the mode itself.

### Press message record

Each message record is identical in shape to a press-light record. The `pass`
field, always `1` in press-light, now ranges `1..N`.

`message_id` is `press:{turn}:{speaker}:{pass}`. The pass component already
makes pass-1 and pass-2 messages from the same speaker distinct IDs, so the
validator's duplicate-ID check handles multi-turn without change.

Each record's `prior_messages` captures exactly what that speaker saw at
decision time: for a pass-2 speaker, this is the entire pass-1 transcript plus
earlier speakers in pass 2. The artifact is a faithful transcript of the
conversation.

### Config additions

`PressConfig` gains a `passes` field:

```json
{
  "press": {"mode": "multi_turn_public", "enabled": true, "passes": 2}
}
```

- `passes` is a positive integer (`>= 1`).
- `passes` is required in the config block when `mode == "multi_turn_public"`.
  It is forbidden (the loader rejects its presence) when `mode` is `none` or
  `press_light`.
- The `PressConfig` dataclass defaults `passes` to `1` so it can coexist with
  press_light and none configs, but the loader enforces the required/forbidden
  rule above, so the default never silently applies to a `multi_turn_public`
  config.
- `PRESS_MODES` gains `"multi_turn_public"`.

### Failure snapshot reuse

Press failures reuse the existing `failure.py` `press_failure()` path unchanged.
`press_failure` already accepts a `pass_no` argument. Multi-turn passes the
actual pass number, so a failure in pass 2 records `pass: 2` in the snapshot.

## Code Layout

Modified files:

- `press_config.py` adds the `passes` field to `PressConfig` and `load_press_config`,
  with strict validation. `passes` is required for `multi_turn_public` and
  forbidden otherwise.
- `config_constants.py` adds `"multi_turn_public"` to `PRESS_MODES`.
- `press_coordinator.py` extracts the current speaker loop from `run_round_press`
  into `_run_pass`, adds a `passes` constructor argument, and loops passes in
  `run_round_press`, threading the accumulating transcript and the actual
  `pass_no` into each speaker call. Press-light constructs the coordinator with
  `passes=1`, so its behavior is unchanged.
- `harness.py` expands the `press_enabled` check to include
  `multi_turn_public`, and passes `config.press.passes` to the coordinator
  when the mode is `multi_turn_public`.

No new files are needed. `press_scene.py`, `press_response.py`, `press_trace.py`,
`press_failure.py`, `press_artifacts.py`, `simulation.py`, `agent.py`, and
`scene.py` are unchanged.

`press_coordinator.py` grows by roughly the pass loop and the `_run_pass`
extraction. It stays under 150 lines; if the extraction would exceed that,
`_run_speaker` moves to its own module.

### Cost note

Each pass adds one model call per living player. A `passes=2` run roughly
doubles the press-call cost versus press-light. The config makes this explicit
and bounded.

## Visualizer

The visualizer needs no functional code change for multi-turn.

- `pressArtifacts.js` already normalizes the `messages` array into conversation
  rows by `message_id`, and `validatePressArtifact` already accepts
  `multi_turn_public` in `PRESS_MODES`.
- The Conversation panel renders messages in array order; multi-turn records
  are already in pass order because the coordinator appends them that way.
- The timeline joins press by turn, which still works (multi-turn has more
  messages per turn).

The raw `pass` field is visible in the Forensic JSON view. A pass-number
display in the Conversation panel is deferred as a UX refinement; this design
does not add it.

The smoke test loads a real multi-turn run's artifacts and confirms the
Conversation tab renders them.

## Error Handling

Multi-turn keeps the strict development behavior from press-light.

Strict failures (same as press-light, now carrying the actual `pass_no`):

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
run fails by default in development mode.

Failure snapshot behavior mirrors the press-light path. A press failure raises
`ConcordiaDecisionFailure`, the harness wraps it as `ConcordiaRunFailure`, and
`concordia/failure_snapshot.json` is written with the press scene, raw visible
responses, parse result, validation errors, provider metadata, sanitized
exception details, and the `pass` number.

## Testing And Verification

Python tests, table-driven and seeded, extending the press-light tests:

- `test_press_config.py` extends to accept `multi_turn_public` with `passes`
  (2, 3); reject `passes=0`, negative, non-int, missing `passes` when mode is
  `multi_turn_public`, and `passes` present when mode is `press_light` or
  `none`. Default config still reproduces press-light/no-press.
- `test_press_coordinator.py` extends to verify that with `passes=2` each living
  speaker produces two records per round with `pass=1` and `pass=2`; that
  pass-2 speakers see pass-1 messages in `prior_messages`; that first-legal
  clients decline on every pass; and that a broken client fails hard with the
  correct `pass_no` in the failure snapshot.
- `test_press_harness.py` integration: a `multi_turn_public` run with `passes=2`,
  four first-legal agents, completes a game; `press_traces.json` is written with
  `press_mode: multi_turn_public`; messages carry `pass` values 1 and 2; replay
  is unchanged; press-disabled still reproduces no-press; fail-hard on a broken
  client.
- Parity gate: press-light behavior is unchanged. A `press_light` run still
  produces `pass=1` only and identical replay to the press-light baseline.

Visualizer:

- The existing `pressArtifacts.test.js` already covers `multi_turn_public`
  acceptance via `PRESS_MODES`. No new unit test is required, but the smoke
  test loads a real multi-turn artifact.
- The smoke test loads the multi-turn demo folder and confirms the Conversation
  tab renders messages.

## Press Mode Ladder

This design implements the multi-turn public press rung.

### No-Press

Agents only choose legal WOPR actions. No communication.

### Press-Light

One public message per round.

### Multi-Turn Public Press

This design. Fixed `N` passes per round, full transcript memory.

### Full Press

Public and private channels, multi-turn negotiation, commitments, threats,
promises, deception, and later violation analysis. The `audience`,
`visibility`, and `linked_decision_traces` seams support this. Not implemented
here.
