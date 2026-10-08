import { describe, expect, it } from 'vitest';
import { traceArtifactPayload, traceReplayPayload } from '../test/replayFixtures.js';
import { summarizeDecisionTrace } from './decisionSummaries.js';

describe('summarizeDecisionTrace', () => {
  it('summarizes schema v4 trace data for readable agent inspection', () => {
    const trace = traceArtifactPayload().traces[0];
    const relatedAction = traceReplayPayload().actions[0];
    const summary = summarizeDecisionTrace(trace, relatedAction);

    expect(summary.selectedActionId).toBe('player_0:draw');
    expect(summary.selectedActionLabel).toBe('Draw');
    expect(summary.decisionType).toBe('draw');
    expect(summary.validationStatus).toBe('Recovered after 1 retry');
    expect(summary.validationErrors).toEqual(['No legal action_id parsed']);
    expect(summary.legalOptionGroups).toEqual([
      { family: 'Player 0', options: [{ actionId: 'player_0:draw', label: 'Draw' }] },
    ]);
    expect(summary.promptPreview).toBe('choose one action');
    expect(summary.responsePreview).toBe('not-json');
    expect(summary.parseResult).toEqual({ action_id: 'player_0:draw', rationale: 'need cards' });
    expect(summary.statedRationale).toBe('need cards');
    expect(summary.provider).toMatchObject({
      label: 'hosted',
      model: 'demo-model',
      latencyMs: 25,
      cost: 0.012,
      usage: { total_tokens: 12 },
    });
  });

  it('returns an empty summary when no trace is linked', () => {
    expect(summarizeDecisionTrace(null, null)).toEqual(null);
  });
});
