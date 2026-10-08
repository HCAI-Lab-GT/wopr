# Concordia Agent Harness Design

Date: 2026-06-22

## Goal

Build a Concordia-first agent harness for WOPR Nuclear War. The first working
milestone is one full AI-only table game with four Concordia-backed seats. WOPR
remains the rules engine and source of legal actions. Concordia supplies agent
identity, memory, situation framing, and action selection.

SiliSocs is not part of the core implementation path for this milestone. It can
remain a future study-orchestration layer if it becomes useful later.

## Scope

Milestone 1 is no-press:

- Four AI-only Concordia-backed seats complete one WOPR table game.
- No human UI is included.
- No communication turns are included.
- WOPR replay JSON remains unchanged.
- Concordia-specific decision context is written to sidecar artifacts.
- Development-mode validation is strict enough to catch integration mistakes.

Actual Concordia runtime integration should be tried first. If runtime import,
setup, or API mismatch blocks progress during the first focused implementation
pass, the implementation should fall back to a Concordia-style adapter with the
same agent-facing concepts and trace shape. The runtime path must be recorded
honestly in run metadata.

## Architecture

The system has four layers.

### WOPR Engine Layer

WOPR keeps the existing decision-machine loop:

- `pending_decision(state)`
- `observe(state, agent_id)`
- `apply_decision(state, action)`

WOPR owns all legal actions, randomization, state mutation, replay events, and
terminal outcomes. WOPR should not depend on Concordia internals.

### Concordia Adapter Layer

The adapter converts WOPR decision points into Concordia-facing scenes. It
provides each agent with:

- stable identity and role metadata,
- current decision type,
- private WOPR observation,
- public game state summary,
- legal WOPR action list,
- prior decision history or memory context when available.

The adapter converts Concordia output back into exactly one WOPR legal action
id. It must reject invented actions.

### Concordia Agent Layer

Milestone 1 uses four AI-only agents. Each agent should have:

- identity,
- situation framing,
- memory or decision history,
- action-selection behavior.

For no-press, agents choose only mechanical WOPR actions. Later press modes add
message production before action selection.

### Trace And Inspection Layer

Replay JSON remains WOPR-owned and unchanged. Concordia-specific data is written
to sidecars. The replay workbench should be able to inspect decision traces
without needing to reconstruct Concordia runtime internals.

## Data Flow

Each no-press decision cycle follows this flow:

1. WOPR advances until a pending decision exists.
2. WOPR emits an observation, legal actions, decision type, turn, player id, and
   decision context.
3. The Concordia adapter renders a scene for the active agent.
4. The Concordia-backed agent chooses one intended action.
5. The adapter validates that the selected action id exactly matches one legal
   WOPR action.
6. WOPR applies the validated action.
7. The trace sidecar records the model-visible or runtime-visible interaction.
8. The loop continues until terminal state or max turns.

For press-light later, one message step is added before mechanical action
choice. The message is public, trace-only, and does not mutate WOPR game state.

## Press Mode Ladder

Press should be added as explicit modes instead of one broad feature.

### No-Press

Agents only choose legal WOPR actions. There is no communication.

### Press-Light

Each active player gets one public communication opportunity at the start of
their player turn. The message is visible to all living players, recorded in a
sidecar, and available to Concordia memory. It does not mutate WOPR state.

### Multi-Turn Public Press

Agents participate in multiple public communication passes before choosing
mechanical WOPR actions. This supports dialogue, threats, persuasion, and
coalition talk without private channels.

### Full Press

Agents can use public and private communication channels. This mode supports
negotiation, deception, commitments, threats, and later violation analysis.
WOPR still owns legal game actions and resolution.

### Human-Interactive Press

Human participation is a later UI and UX layer. Humans should use the same
press/action interfaces as AI agents.

## Error Handling

Development mode should fail fast on integration problems and allow only limited
recovery for model formatting errors.

Strict failures:

- Concordia import or setup failure, unless the run explicitly enters the
  Concordia-style fallback path.
- Missing required Concordia agent metadata.
- Failure to render a valid Concordia-facing scene.
- Failure to map Concordia output back to WOPR action ids.
- Trace schema validation failure.
- WOPR engine exception.
- Selected action, replay action, or trace action mismatch.

Recoverable once:

- malformed model output,
- empty model output,
- selected action id not in legal options,
- provider timeout or HTTP error.

For recoverable cases, retry once with validation feedback. If retry fails, the
run fails by default in development mode. A configured fallback action may exist
later, but it should not be enabled by default for Concordia development runs.

Retry layering: this "retry once" is the *decision-agent* budget. It composes
with a lower-level transport retry — the OpenAI-compatible HTTP client retries
transient HTTP *statuses* (429/5xx) up to three times with no backoff, because
those are load/rate signals where re-issuing the same idempotent request is
standard. The `ConcordiaDecisionAgent` then retries a *failed transport call*
(socket timeout, connection drop, or a non-retryable HTTP error) at most once
more within its `max_retries` budget. Config faults (missing base_url/model/API
key) surface as `LLMConfigError` and stay strictly fatal — retrying never helps.
Each recoverable retry is recorded on the decision trace via a dedicated
`recoverable_provider_retries` counter (distinct from `retries`, which counts
model round-trips, and kept out of `validation_errors`/the invalid-output tally).
It aggregates both layers — the transport client's internal 429/5xx retries and
the agent's re-issue of a failed transport call — so all recoverable provider
retries stay observable without being counted as bad model output.

Milestone 1 success requires a completed game with no integration failures, no
trace validation failures, and no fallback-selected actions.

## Artifacts

Milestone 1 should write:

- `wopr/replay.json`: unchanged WOPR replay payload.
- `wopr/traces.json`: Concordia decision trace sidecar.
- `concordia/config_snapshot.json`: run and agent config.
- `concordia/agent_metadata.json`: per-agent identity, role, components, and
  model/client metadata.
- `concordia/run_summary.json`: outcome, turns, trace counts, invalid outputs,
  retries, fallback count, and runtime path.

Each decision trace should include:

- trace id,
- player id,
- turn,
- decision type,
- WOPR rendered observation,
- legal WOPR options,
- Concordia scene or structured context,
- Concordia agent identity fields used for the decision,
- raw runtime or model response,
- parse result,
- selected WOPR action id,
- validation errors,
- retry count,
- fallback used flag,
- provider/model latency and usage if available.

Press-light later adds `concordia/press_traces.json` with message id, turn,
speaker, audience, visibility, text, and linked decision trace when applicable.

## Testing And Verification

Unit tests:

- Concordia config parsing.
- Agent metadata validation.
- WOPR observation to Concordia scene rendering.
- Concordia output parsing.
- Legal action validation.
- Strict failure on invalid or missing action after retry.
- Trace artifact validation.

Integration tests:

- Four scripted Concordia-style agents complete a deterministic game without
  network access.
- One failing scripted agent causes the run to fail in development mode.
- Four LLM-backed Concordia agents are env-gated and skipped unless required
  provider settings are present.

Live smoke:

- Four real Concordia-backed agents complete one game.
- Replay and trace sidecars validate.
- No fallback-selected actions occur.
- Summary records runtime path as either `concordia_runtime` or
  `concordia_style_fallback`.

Visualizer check:

- Existing replay workbench loads the replay.
- Decision tab can inspect Concordia traces.
- Later press traces are visible in a message timeline or transcript view.
