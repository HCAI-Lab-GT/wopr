import { describe, expect, it } from 'vitest';
import { attachTraceFrames, parseTraceArtifactJson } from './traceArtifacts.js';

const REPLAY = {
  mode: 'table',
  seed: 5,
  agent: 'decision_heuristic',
  players: 2,
  turns: 1,
  winner: null,
  termination_reason: 'max_turns',
  final_populations: { player_0: 25, player_1: 25 },
  actions: [
    {
      action_id: 'player_0:draw',
      action_type: 'draw',
      payload: {},
      player_id: 'player_0',
      turn: 1,
    },
  ],
  events: [
    {
      card_id: 'card_1',
      event_type: 'card_drawn',
      payload: {},
      player_id: 'player_0',
      turn: 1,
    },
  ],
};

const TRACE = {
  trace_id: 'player_0:1:1',
  turn: 1,
  player_id: 'player_0',
  decision_type: 'draw',
  rendered_observation: { player_id: 'player_0', decision_type: 'draw' },
  prompt: 'choose one action',
  prompts: ['choose one action'],
  legal_options: [{ action_id: 'player_0:draw' }],
  raw_response: '{"action_id":"player_0:draw"}',
  raw_responses: ['{"action_id":"player_0:draw"}'],
  parse_result: { action_id: 'player_0:draw', rationale: null },
  selected_action_id: 'player_0:draw',
  retries: 0,
  validation_errors: [],
  stated_rationale: null,
  provider_latency_ms: 12,
  provider_cost: 0.003,
  provider_usage: { prompt_tokens: 8, completion_tokens: 4 },
  provider_label: 'hosted',
  provider_model: 'demo-model',
  fallback_used: false,
  recoverable_provider_retries: 0,
};

function artifact(trace = TRACE, schemaVersion = 5) {
  return {
    schema_version: schemaVersion,
    replay: {
      mode: REPLAY.mode,
      seed: REPLAY.seed,
      agent: REPLAY.agent,
      players: REPLAY.players,
      turns: REPLAY.turns,
    },
    traces: [trace],
  };
}

describe('trace artifacts', () => {
  it('parses trace artifacts and attaches traces to matching frames', () => {
    const traceArtifact = parseTraceArtifactJson(JSON.stringify(artifact()), REPLAY);
    const frames = attachTraceFrames(
      [
        { eventIndex: 0, relatedAction: null },
        { eventIndex: 1, relatedAction: REPLAY.actions[0] },
      ],
      traceArtifact,
    );

    expect(traceArtifact.traces).toHaveLength(1);
    expect(traceArtifact.traces[0].rendered_observation.player_id).toBe('player_0');
    expect(traceArtifact.traces[0].provider_latency_ms).toBe(12);
    expect(traceArtifact.traces[0].provider_cost).toBe(0.003);
    expect(traceArtifact.traces[0].provider_usage.total_tokens).toBeUndefined();
    expect(traceArtifact.traces[0].provider_model).toBe('demo-model');
    expect(frames[0].decisionTrace).toBeNull();
    expect(frames[1].decisionTrace.prompt).toBe('choose one action');
  });

  it('rejects unlinked trace selected actions', () => {
    const badTrace = {
      ...TRACE,
      selected_action_id: 'missing-action',
      legal_options: [{ action_id: 'missing-action' }],
    };

    expect(() => parseTraceArtifactJson(JSON.stringify(artifact(badTrace)), REPLAY)).toThrow(
      /does not link to replay action/,
    );
  });

  it('rejects selected actions missing from legal options', () => {
    const badTrace = { ...TRACE, legal_options: [{ action_id: 'different-action' }] };

    expect(() => parseTraceArtifactJson(JSON.stringify(artifact(badTrace)), REPLAY)).toThrow(
      /selected_action_id missing from legal_options/,
    );
  });

  it('parses a v5 artifact carrying fallback_used and recoverable_provider_retries', () => {
    const trace = { ...TRACE, fallback_used: true, recoverable_provider_retries: 2 };
    const traceArtifact = parseTraceArtifactJson(JSON.stringify(artifact(trace)), REPLAY);

    expect(traceArtifact.traces[0].fallback_used).toBe(true);
    expect(traceArtifact.traces[0].recoverable_provider_retries).toBe(2);
  });

  it('still accepts legacy v4 artifacts without the v5 fields', () => {
    const { fallback_used, recoverable_provider_retries, ...v4Trace } = TRACE;
    void fallback_used;
    void recoverable_provider_retries;

    const traceArtifact = parseTraceArtifactJson(
      JSON.stringify(artifact(v4Trace, 4)),
      REPLAY,
    );

    expect(traceArtifact.traces).toHaveLength(1);
  });

  it('rejects a v5 trace missing recoverable_provider_retries', () => {
    const { recoverable_provider_retries, ...badTrace } = TRACE;
    void recoverable_provider_retries;

    expect(() => parseTraceArtifactJson(JSON.stringify(artifact(badTrace)), REPLAY)).toThrow(
      /missing required field: recoverable_provider_retries/,
    );
  });

  it('rejects a v5 trace with a non-boolean fallback_used', () => {
    const badTrace = { ...TRACE, fallback_used: 'yes' };

    expect(() => parseTraceArtifactJson(JSON.stringify(artifact(badTrace)), REPLAY)).toThrow(
      /fallback_used must be a boolean/,
    );
  });
});
