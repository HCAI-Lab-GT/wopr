export function unsupportedReplay() {
  return JSON.stringify(unsupportedReplayPayload());
}

export function traceReplay() {
  return JSON.stringify(traceReplayPayload());
}

export function traceArtifact() {
  return JSON.stringify(traceArtifactPayload());
}

export function unsupportedReplayPayload() {
  return {
    mode: 'table',
    seed: 9,
    agent: 'test',
    players: 2,
    turns: 1,
    winner: null,
    termination_reason: 'test',
    final_populations: { player_0: 25, player_1: 25 },
    actions: [
      {
        action_id: 'player_0:advance',
        action_type: 'advance',
        payload: {},
        player_id: 'player_0',
        turn: 1,
      },
    ],
    events: [
      {
        card_id: null,
        event_type: 'frontend_unknown_event',
        payload: {},
        player_id: 'player_0',
        turn: 1,
      },
    ],
  };
}

export function traceReplayPayload() {
  return {
    mode: 'table',
    seed: 5,
    agent: 'decision_heuristic',
    players: 2,
    turns: 1,
    winner: null,
    termination_reason: 'max_turns',
    final_populations: { player_0: 25, player_1: 25 },
    actions: [{ action_id: 'player_0:draw', action_type: 'draw', payload: {}, player_id: 'player_0', turn: 1 }],
    events: [{ card_id: 'card_1', event_type: 'card_drawn', payload: {}, player_id: 'player_0', turn: 1 }],
  };
}

export function traceArtifactPayload() {
  return {
    schema_version: 5,
    replay: { mode: 'table', seed: 5, agent: 'decision_heuristic', players: 2, turns: 1 },
    traces: [
      {
        trace_id: 'player_0:1:1',
        turn: 1,
        player_id: 'player_0',
        decision_type: 'draw',
        rendered_observation: { player_id: 'player_0', decision_type: 'draw' },
        prompt: 'choose one action',
        prompts: ['choose one action'],
        legal_options: [{ action_id: 'player_0:draw', label: 'Draw' }],
        raw_response: 'not-json',
        raw_responses: ['not-json', '{"action_id":"player_0:draw"}'],
        parse_result: { action_id: 'player_0:draw', rationale: 'need cards' },
        selected_action_id: 'player_0:draw',
        retries: 1,
        validation_errors: ['No legal action_id parsed'],
        stated_rationale: 'need cards',
        provider_latency_ms: 25,
        provider_cost: 0.012,
        provider_usage: { prompt_tokens: 8, completion_tokens: 4, total_tokens: 12 },
        provider_label: 'hosted',
        provider_model: 'demo-model',
        fallback_used: false,
        recoverable_provider_retries: 0,
      },
    ],
  };
}
