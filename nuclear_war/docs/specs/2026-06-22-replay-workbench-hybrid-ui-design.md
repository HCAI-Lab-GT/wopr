# Replay Workbench Hybrid UI Design
Date: 2026-06-22

## Goal
Improve `wopr_visualizer` so Concordia and future press runs read as game
replays first, while full replay, trace, prompt, response, runtime, and failure
data remain inspectable.

The current Inspector defaults to raw JSON. The next version separates readable
game comprehension from exact payload inspection.

## Scope
In scope:
- Hybrid `Game` and `Forensic` modes.
- Game tabs: `Event`, `Agent`, and `Conversation`.
- Clear event and decision summaries with icons and normal capitalization.
- Raw JSON and trace access preserved in Forensic mode.
- Extension points for press-light, multi-turn public press, full press, and
  strict failure snapshots.

Out of scope:
- WOPR replay schema changes.
- Concordia trace schema changes.
- Press mechanics.
- Human play UI.
- Fake agent thoughts, hidden chain-of-thought, or placeholder conversations.

## Visual Direction
Use a restrained strategic war-room style: dark map material, amber command
accents, clear player state, and direct labels. The board remains dominant.
Raw data is available through deliberate inspection controls, not the default
reading path.

Icons should improve scanning, not decorate. Use them for event, player,
decision, warning, runtime, prompt, response, legal options, conversation, and
raw data markers.

## Layout
Keep the existing top import/status bar, board, right inspector, population
chart, and bottom timeline.

The right inspector becomes:
1. Mode switch: `Game` and `Forensic`.
2. Game tabs: `Event`, `Agent`, and `Conversation`.

The selected event, timeline marker, and board frame are shared across all
modes and tabs. Switching modes or tabs must not change the selected event.

## Game Mode
Game mode is the default. It answers: what happened in the game?

`Event` is the default tab. It shows deterministic summaries derived from
replay fields: event story, affected players, population changes, queue/card
changes, combat consequences, reducer warnings, and links to related action,
agent trace, conversation, and raw data. It must not invent motives.

Example:
> Commander 3 advanced the launch queue. No population changed, but one delivery
> card moved closer to resolution.

`Agent` shows the linked decision trace in readable form: player identity,
decision type, selected action, validation status, retry count, legal options
grouped by action family where possible, short stated rationale if present,
prompt/response previews, and provider/runtime metadata. Native Concordia runs
should clearly show `concordia_runtime` versus `concordia_style_fallback`,
invalid output count, retry count, and fallback count.

`Conversation` is reserved for press artifacts. No-press runs show:
> No press messages in this replay.

Press-light should show public statements with turn, speaker, audience, and
linked decision. Multi-turn public press should show chronological public
threads. Full press should add public/private visibility, commitments, threats,
and later violation markers. These must come from traceable artifacts, not
inferred hidden reasoning.

## Forensic Mode
Forensic mode is for debugging and audit. It contains replay event JSON, related
action JSON, decision trace JSON, rendered observation, legal options, prompt
history, raw response history, parse result, validation errors, provider
metadata, runtime metadata, and loaded failure snapshot data.

Forensic mode can use code blocks and JSON viewers. It is not the default view.

## Failure And Folder Loading
The UI should support `concordia/failure_snapshot.json` as a separate load path
or as part of Concordia demo-folder import. A failure view should show failed
player, turn, decision type, legal options, prompt or scene payload, raw visible
response, validation errors, provider metadata, and sanitized exception details.

Demo-folder import should read:
- `wopr/replay.json`
- `wopr/traces.json`
- `concordia/run_summary.json`
- `concordia/runtime_status.json`
- `concordia/agent_metadata.json`
- `concordia/config_snapshot.json`
- optional `concordia/failure_snapshot.json`

## Timeline
The timeline remains the navigation spine and gains marker types for event,
decision, warning, launch, detonation, elimination, press message, and failure.
Press markers should be visible even when the Conversation tab is closed.

## Data Boundaries
The UI must label sources clearly:
- replay events are WOPR game facts,
- decision traces are agent interaction records,
- conversation traces are press artifacts,
- failure snapshots are incomplete-run diagnostics,
- Forensic mode is the source for exact raw payloads.

## Component Plan
Likely changes:
- `Inspector`: mode and tab shell.
- `GameInspector`: game tab routing.
- `EventStoryPanel`: event consequences.
- `AgentDecisionPanel`: trace and decision summary.
- `ConversationPanel`: no-press state and future press traces.
- `ForensicPanel`: raw JSON sections.
- `RunMetadataPanel`: Concordia runtime and summary metadata.

Pure helpers should live under `src/replay/` for event stories, option grouping,
trace summaries, future conversation normalization, and failure snapshots.

## Testing
Tests should cover event story summaries, no-press Conversation state, Agent tab
trace summaries, Forensic raw sections, runtime summary display, mode/tab
switching without losing selected frame, and failure snapshot parsing once
loading exists.

Smoke tests should load sample and Concordia replay/traces, switch `Game` and
`Forensic`, switch `Event`, `Agent`, and `Conversation`, verify the board
remains visible, and verify raw JSON is only in Forensic by default.

## Implementation Notes
Do not rebuild the whole app. Reuse the existing board, timeline, import flow,
trace linking, and replay reducer. The `Conversation` tab and timeline marker
model are the main extension points for press-light, multi-turn public press,
and full press.
