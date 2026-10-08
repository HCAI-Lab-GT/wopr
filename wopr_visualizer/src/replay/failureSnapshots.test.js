import { describe, expect, it } from 'vitest';
import { parseFailureSnapshotJson } from './failureSnapshots.js';

function validSnapshot() {
  return {
    config_snapshot: { runtime: 'concordia_runtime', api_key_env: 'TOGETHER_API_KEY' },
    runtime_status: { runtime_path: 'concordia_runtime' },
    agent_metadata: { player_0: { agent: 'concordia_native_http' } },
    decision_failure: {
      agent_identity: { name: 'Analyst Zero' },
      player_id: 'player_0',
      turn: 1,
      decision_type: 'pass',
      scene_payload: { scene_text: 'Choose an action.' },
      legal_options: [{ action_id: 'player_0:draw', label: 'Draw' }],
      prompts: ['Choose an action.'],
      raw_visible_responses: ['not-json'],
      parse_result: { action_id: null, rationale: null },
      validation_errors: ['No action_id parsed'],
      provider_metadata: { provider_label: 'hosted' },
      exception: { type: 'ValueError', message: 'bad response' },
    },
  };
}

describe('parseFailureSnapshotJson', () => {
  it('parses a strict failure snapshot and preserves debug fields', () => {
    const parsed = parseFailureSnapshotJson(JSON.stringify(validSnapshot()));

    expect(parsed.decision_failure.player_id).toBe('player_0');
    expect(parsed.decision_failure.legal_options).toHaveLength(1);
    expect(parsed.decision_failure.validation_errors).toEqual(['No action_id parsed']);
  });

  it.each([
    ['{', /not valid JSON/],
    [JSON.stringify({ decision_failure: { legal_options: [] } }), /agent_identity/],
    [JSON.stringify({ decision_failure: { agent_identity: {}, legal_options: null } }), /legal_options/],
    [JSON.stringify({ ...validSnapshot(), decision_failure: { ...validSnapshot().decision_failure, api_key: 'secret' } }), /secret-shaped/],
    [JSON.stringify({ ...validSnapshot(), decision_failure: { ...validSnapshot().decision_failure, token: 'secret' } }), /secret-shaped/],
  ])('rejects invalid snapshot payload %#', (text, message) => {
    expect(() => parseFailureSnapshotJson(text)).toThrow(message);
  });
});
