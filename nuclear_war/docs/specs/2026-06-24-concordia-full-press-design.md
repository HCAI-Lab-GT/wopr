# Concordia Full Press Design

Date: 2026-06-24

## Goal

Add full press as the final rung of the press ladder, on top of multi-turn
public press. Each completed round, all living agents participate in a
fixed `N` communication passes before the next round's mechanical action
selection. Agents can speak publicly (to all living players) or whisper
privately (to one named recipient). Each agent's press memory is
privacy-filtered: a player sees only public messages plus private messages they
sent or received. The sidecar artifact records the full omniscient transcript
for the researcher; each message's `prior_messages` records the filtered view
that speaker saw.

Speakers can optionally attach a structured commitment to a message. Commitments
are recorded as data and linked to later decisions via `linked_decision_traces`.
No automatic violation detection runs in this design; that analysis is
performed by the researcher against the artifact after the game.

WOPR remains the only rules engine and the source of legal actions. Press is
still trace-only. It never mutates WOPR game state, and the replay JSON stays
unchanged.

## Decisions

These decisions were made during planning:

1. Single-recipient private channels. A private message has one explicit
   recipient. Only the speaker and that recipient see it in their `press_memory`;
   other players never do.
2. Discrete options plus a recipient field for channel choice. The legal_options
   list expands to `decline`, `speak`, `whisper`. When the model chooses
   `whisper`, it also specifies a `to` recipient. The parser extracts the
   recipient from the JSON.
3. Omniscient sidecar, filtered per-speaker `prior_messages`. The sidecar
   records every message (public and private) with full content. Each message's
   `prior_messages` records only what that speaker legitimately saw.
4. Structured commitments recorded, no auto-detection. A commitment is a small
   object `{kind, target_round?, notes?}` the model optionally emits. Recorded
   in the sidecar. No violation detection or enforcement runs.
5. Reuse the multi-turn fixed-N pass model. `press.passes` drives the pass count,
   same as `multi_turn_public`.

## Scope

In scope:

- A new `full_press` press mode with private (single-recipient) channels.
- A privacy filter `visible_to(player, transcript)` that each agent's memory
  passes through.
- Discrete `decline` / `speak` / `whisper` options, with the parser extracting
  recipient and optional commitment from the model output.
- Omniscient sidecar with privacy-filtered per-message `prior_messages`.
- Structured commitment recording (data only, no enforcement).
- Config validation that `passes` is required for `full_press` (same rule as
  `multi_turn_public`).
- A `full_press` example config and harness integration test.
- Visualizer rendering of private messages and commitment badges.

Out of scope:

- WOPR replay schema changes.
- Any new WOPR `ActionType`, `EngineEvent`, or entry in `replay["actions"]`.
- Automatic commitment violation detection or enforcement. That is analysis the
  researcher runs later against the artifact.
- Multi-recipient private channels (coalitions, cabals).
- Broadcast-except-one channels.
- Dynamic termination by vote or silence.
- Per-player message budgets.
- Any rule-level consequence of speech. Speech never mutates game state.
- Human play.
- Batch runner changes. `full_press` is single-game `concordia-demo` only.
- Any change to press-light or multi-turn behavior or artifacts.
- Native Concordia press message production. HTTP remains the press producer.

## Architecture

Full press is an additive extension of the multi-turn coordinator. The pass
loop, transcript threading, and `pass_no` handling are reused unchanged. What is
new: the speaker's options include a private channel with a recipient; the
parser extracts the recipient and an optional commitment; and each agent's view
of the transcript is privacy-filtered by `visible_to`.

The dependency direction stays concordia -> wopr. The only engine contact
remains the single optional `press_hook` callback in `simulation.py`, which is
unchanged. WOPR never imports anything from `nuclear_war_concordia`.

### Privacy boundary

The privacy rule is expressed in one function, `visible_to(player, transcript)`,
in a new module `press_visibility.py`:

- All messages with `visibility == "public"` are visible.
- Messages with `visibility == "private"` are visible only when `player` is the
  `speaker` or the `recipient`.

The coordinator keeps the full omniscient transcript (all messages, all
audiences) as the source of truth. When rendering a speaker's scene, it passes
`visible_to(speaker, transcript)` as `prior_messages`. When recording a message,
it stores `visible_to(speaker, transcript)` in that message's `prior_messages`
field. The omniscient transcript goes to the sidecar untouched.

### Data flow

Each full-press round:

1. The table loop completes a full round and reaches `at_round_boundary`.
2. The loop checks termination. If the game continues, before `resume_round` it
   calls `press_hook(state, completed_round)` when configured.
3. The `PressCoordinator` runs `passes` communication passes. For each pass `p`
   in `1..N`:
   1. It iterates living speakers in clockwise turn order.
   2. For each speaker, it renders a press scene from the speaker's observation,
      identity, the privacy-filtered view of the transcript so far, and the
      full-press option set (`decline`, `speak`, `whisper`).
   3. The speaker's Concordia client produces one response.
   4. The adapter parses the response into a visibility (`public` or
      `private`), an optional recipient, the message text, an optional
      rationale, and an optional commitment.
   5. A full-parity press trace is appended with `pass=p`, the recipient (if
      private), and the commitment (if any). The message's `prior_messages` is
      the privacy-filtered view the speaker saw.
   6. The message is appended to the omniscient transcript.
4. The coordinator returns the transcript to the harness. The harness attaches
   a privacy-filtered per-player view to each agent's `press_memory`.
5. The loop resumes the next round. Action selection proceeds with the filtered
   transcript present in each decision scene.

### Memory injection

Memory injection works as in press-light and multi-turn. Each
`ConcordiaDecisionAgent` holds a `press_memory` list of messages it has seen.
For full press, the harness builds per-agent filtered views using `visible_to`,
so each agent's decision scene contains only the messages it is permitted to
see. Empty or absent `press_memory` still reproduces the no-press scene.

## Artifacts

### `concordia/press_traces.json`

The sidecar wrapper is structurally identical to prior rungs. `press_mode` is
`"full_press"`.

```json
{
  "schema_version": 1,
  "press_mode": "full_press",
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

The validator already accepts `full_press` in `PRESS_MODES`.

### Press message record

Two new optional fields support private channels and commitments. The
`audience` and `visibility` fields, always `public` until now, now carry real
values.

```json
{
  "message_id": "press:2:player_0:1",
  "turn": 2,
  "round": 2,
  "speaker": "player_0",
  "audience": "player_1",
  "visibility": "private",
  "recipient": "player_1",
  "pass": 1,
  "decision_type": "press",
  "commitment": {
    "kind": "stand_down",
    "target_round": 3,
    "notes": "will not launch this round"
  },
  "prior_messages": [],
  "linked_decision_traces": []
}
```

- `recipient` (optional): present only when `visibility == "private"`. A single
  player id. Required when private, forbidden when public.
- `commitment` (optional, nullable): present only when the model emitted one.
  An object `{kind, target_round?, notes?}`:
  - `kind`: a short free-text label the model provides (e.g. `"stand_down"`,
    `"ally_with"`, `"target"`, `"no_first_use"`). Not an enum. The model names
    the commitment; the researcher interprets it.
  - `target_round`: optional positive integer, the round by which the
    commitment applies.
  - `notes`: optional free-text elaboration.

The channel is fully described by `visibility` (`public` or `private`) plus
`audience` (`public` or the recipient player id). No separate `channel` field.

`linked_decision_traces` remains an empty array in this design. It is the
hook the researcher uses post-hoc to link a commitment to later decisions. Its
presence is required (validated), its content is `[]`.

### Privacy in `prior_messages`

Each message's `prior_messages` records only what that speaker legitimately saw
at decision time, computed by `visible_to(speaker, transcript)`:

- All `visibility == "public"` messages.
- All `visibility == "private"` messages where `speaker == player` OR
  `recipient == player`.

A private whisper from player_0 to player_1 appears in player_0's and
player_1's `prior_messages` in later scenes, but never in player_2's or
player_3's. The omniscient `messages` array in the sidecar contains it
regardless, for the researcher.

### Config

```json
{
  "press": {"mode": "full_press", "enabled": true, "passes": 2}
}
```

`passes` is required for `full_press` (same rule as `multi_turn_public`),
defaulting to `1` on the dataclass. `PRESS_MODES` already contains `full_press`.
The loader's `passes` validation extends to treat `full_press` like
`multi_turn_public`.

### Failure snapshot reuse

Press failures reuse the existing `failure.py` `press_failure()` path
unchanged. `press_failure` accepts `pass_no`. The recipient rides along in the
scene payload already recorded.

## Code Layout

New files in `nuclear_war/src/nuclear_war_concordia/`:

- `press_visibility.py` provides `visible_to(player, transcript)`. The entire
  privacy rule, isolated and unit-testable.
- `press_commitment.py` provides `parse_commitment(payload)`. Validates an
  optional `{kind, target_round?, notes?}` object or returns `None`.
- `press_speaker.py` holds the single-speaker flow extracted from
  `press_coordinator.py`, so the coordinator stays under 150 lines.

Modified files:

- `press_scene.py` gains an optional `options` argument. The coordinator passes
  the full-press option set when mode is `full_press`, the existing pair
  otherwise. The prompt text describes the whisper channel and the optional
  commitment field only when full-press options are present.
- `press_response.py` extends `parse_press_response` to handle `whisper`,
  extract the recipient from `to`, and parse the optional `commitment`.
- `press_trace.py` records `recipient` and `commitment` on the trace record.
  `prior_messages` is computed by the coordinator via `visible_to` and passed
  in.
- `press_coordinator.py` gains a `mode` constructor argument. For `full_press`
  it builds the full-press option set, uses `visible_to` instead of `_visible`,
  and threads `recipient` and `commitment` through the transcript and trace. For
  other modes behavior is unchanged. `_run_speaker` moves to `press_speaker.py`.
- `press_config.py` extends the `passes`-required rule to `full_press`.
- `types.py` adds `recipient` and `commitment` to `ParsedPressMessage`.
- `press_artifacts.py` validates: `recipient` required when `visibility ==
  "private"` and forbidden when `visibility == "public"`; `commitment` shape
  when present.
- `harness.py` adds `"full_press"` to the enabled modes and passes
  `mode=config.press.mode` to the coordinator.

No change to `simulation.py`, `agent.py`, `scene.py`, `failure.py`, the WOPR
engine, or the replay schema.

### File-size discipline

`press_coordinator.py` is the growth risk. Extracting `_run_speaker` to
`press_speaker.py` keeps the coordinator as the pass orchestrator (~80 lines)
and `press_speaker.py` as the single-speaker flow (~120 lines), both under 150.

### Visualizer changes

- `pressArtifacts.js` includes `recipient` and `commitment` in the normalized
  row.
- `ConversationPanel.jsx` renders private messages distinctly (e.g.
  "player_0 whispered to player_1") and shows a commitment badge when present.
- No validator change needed (`full_press` already accepted).

## Error Handling

Full press keeps strict development behavior.

Strict failures (raise, write failure snapshot):

- Whisper chosen with no recipient.
- Whisper recipient is not a living player.
- Whisper recipient is the speaker.
- Provider error during a press call.
- Trace schema validation failure (recipient required when private; forbidden
  when public).

Recoverable once (retry with feedback, then fail hard):

- Malformed model output (not valid JSON).
- Whisper with an unparseable recipient.

Soft drop (do not fail, log a validation note):

- A valid message whose `commitment` object is well-formed but semantically odd
  (e.g. `target_round` in the past). The commitment is dropped from the trace,
  the message stands, and `validation_errors` records the drop. A malformed
  commitment does not invalidate the message itself.

## Testing And Verification

Python tests, table-driven and seeded, extending the press tests:

- `test_press_visibility.py` (new): `visible_to` returns public always; private
  only when player is sender or recipient; empty for a player with no messages;
  correctly excludes private messages between other players.
- `test_press_commitment.py` (new): `parse_commitment` accepts a valid object;
  rejects empty `kind`, non-int `target_round`, extra fields; returns `None` for
  absent.
- `test_press_config.py` (extend): `full_press` accepts `passes`; rejects `0`,
  missing, wrong type.
- `test_press_response.py` (extend): parses `whisper` with `to` into
  visibility=private, recipient; parses `speak` as public; `decline`; optional
  nested `commitment`; rejects whisper with no recipient; rejects whisper to
  self.
- `test_press_trace.py` (extend): full-press record carries `recipient` and
  `commitment`; public records omit recipient.
- `test_press_coordinator.py` (extend): full_press builds whisper option;
  private messages deliver only to sender+recipient; public to all; first-legal
  declines; broken client fails hard with correct `pass_no`.
- `test_press_artifacts.py` (extend): accepts `full_press`; rejects private
  without recipient; rejects public with recipient; validates commitment shape.
- `test_press_harness.py` (integration, extend): `full_press` run with passes=2
  completes; sidecar has `press_mode: full_press`; messages include public and
  private; private `prior_messages` exclude them from non-participants; replay
  unchanged; fail-hard on whisper without recipient.
- Parity gate: press-light and multi-turn replays still byte-identical to
  no-press.

Visualizer:

- `pressArtifacts.test.js` extends to normalize private messages with recipient
  and render commitment.
- `ConversationPanel.test.jsx` shows "whispered to player_1" for private and a
  commitment badge.
- Smoke loads full_press demo artifacts and renders Conversation tab without
  errors.

### Open verification point

Whether the model reliably produces well-formed whisper responses with a valid
recipient on the first try is not verified until the live run. The live run is
the checkpoint that surfaces this.

## Press Mode Ladder

This design implements the full press rung.

### No-Press

Agents only choose legal WOPR actions. No communication.

### Press-Light

One public message per round.

### Multi-Turn Public Press

Fixed `N` passes per round, full transcript memory.

### Full Press

This design. Public and single-recipient private channels, multi-pass
negotiation, structured commitments recorded without auto-detection,
omniscient sidecar with privacy-filtered per-speaker memory.
