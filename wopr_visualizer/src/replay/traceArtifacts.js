const TRACE_SCHEMA_VERSION = 5;
const SUPPORTED_TRACE_SCHEMA_VERSIONS = Array.from(
  { length: TRACE_SCHEMA_VERSION },
  (_, index) => index + 1,
);
const REQUIRED_ARTIFACT_FIELDS = ['schema_version', 'replay', 'traces'];
const REQUIRED_TRACE_FIELDS_V1 = [
  'trace_id',
  'turn',
  'player_id',
  'decision_type',
  'prompt',
  'prompts',
  'legal_options',
  'raw_response',
  'raw_responses',
  'parse_result',
  'selected_action_id',
  'retries',
  'validation_errors',
  'stated_rationale',
];
const REQUIRED_TRACE_FIELDS_V2 = [
  ...REQUIRED_TRACE_FIELDS_V1,
  'provider_latency_ms',
  'provider_cost',
];
const REQUIRED_TRACE_FIELDS_V3 = [
  ...REQUIRED_TRACE_FIELDS_V2,
  'rendered_observation',
];
const REQUIRED_TRACE_FIELDS_V4 = [
  ...REQUIRED_TRACE_FIELDS_V3,
  'provider_usage',
  'provider_label',
  'provider_model',
];
const REQUIRED_TRACE_FIELDS_V5 = [
  ...REQUIRED_TRACE_FIELDS_V4,
  'fallback_used',
  'recoverable_provider_retries',
];

export function parseTraceArtifactJson(text, replay) {
  let payload;
  try {
    payload = JSON.parse(text);
  } catch (error) {
    throw new Error(`Trace artifact is not valid JSON: ${error.message}`, { cause: error });
  }
  return validateTraceArtifact(payload, replay);
}

export function validateTraceArtifact(payload, replay) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new Error('Trace artifact must be a JSON object.');
  }
  for (const field of REQUIRED_ARTIFACT_FIELDS) {
    if (!(field in payload)) {
      throw new Error(`Trace artifact missing required field: ${field}`);
    }
  }
  if (!SUPPORTED_TRACE_SCHEMA_VERSIONS.includes(payload.schema_version)) {
    throw new Error('Trace artifact schema_version is invalid.');
  }
  if (!matchesReplayReference(payload.replay, replay)) {
    throw new Error('Trace artifact replay reference does not match replay.');
  }
  if (!Array.isArray(payload.traces)) {
    throw new Error('Trace artifact traces must be an array.');
  }
  payload.traces.forEach((trace, index) => validateTrace(trace, index, replay.actions, payload.schema_version));
  return payload;
}

export function attachTraceFrames(frames, traceArtifact) {
  const traces = traceArtifact?.traces ?? [];
  return frames.map((frame) => ({
    ...frame,
    decisionTrace: findTraceForAction(traces, frame.relatedAction),
  }));
}

function validateTrace(trace, index, actions, schemaVersion) {
  if (!trace || typeof trace !== 'object' || Array.isArray(trace)) {
    throw new Error(`Trace ${index} must be a JSON object.`);
  }
  for (const field of requiredTraceFields(schemaVersion)) {
    if (!(field in trace)) {
      throw new Error(`Trace ${index} missing required field: ${field}`);
    }
  }
  if (schemaVersion >= 2) validateProviderMetadata(trace, index);
  if (schemaVersion >= 3) validateRenderedObservation(trace, index);
  if (schemaVersion >= 4) validateProviderTraceMetadata(trace, index);
  if (schemaVersion >= 5) validateRecoveryTraceMetadata(trace, index);
  if (!Number.isInteger(trace.turn) || trace.turn < 0) {
    throw new Error(`Trace ${index} turn must be a nonnegative integer.`);
  }
  if (typeof trace.selected_action_id !== 'string') {
    throw new Error(`Trace ${index} selected_action_id must be a string.`);
  }
  validateLegalOptions(trace, index);
  if (!findMatchingAction(actions, trace)) {
    throw new Error(`Trace ${index} selected_action_id does not link to replay action.`);
  }
}

function requiredTraceFields(schemaVersion) {
  if (schemaVersion === 1) return REQUIRED_TRACE_FIELDS_V1;
  if (schemaVersion === 2) return REQUIRED_TRACE_FIELDS_V2;
  if (schemaVersion === 3) return REQUIRED_TRACE_FIELDS_V3;
  if (schemaVersion === 4) return REQUIRED_TRACE_FIELDS_V4;
  return REQUIRED_TRACE_FIELDS_V5;
}

function validateRecoveryTraceMetadata(trace, index) {
  if (typeof trace.fallback_used !== 'boolean') {
    throw new Error(`Trace ${index} fallback_used must be a boolean.`);
  }
  if (
    !Number.isInteger(trace.recoverable_provider_retries) ||
    trace.recoverable_provider_retries < 0
  ) {
    throw new Error(`Trace ${index} recoverable_provider_retries must be a nonnegative integer.`);
  }
}

function validateProviderMetadata(trace, index) {
  if (trace.provider_latency_ms !== null && !Number.isInteger(trace.provider_latency_ms)) {
    throw new Error(`Trace ${index} provider_latency_ms must be null or integer.`);
  }
  if (trace.provider_cost !== null && typeof trace.provider_cost !== 'number') {
    throw new Error(`Trace ${index} provider_cost must be null or number.`);
  }
}

function validateRenderedObservation(trace, index) {
  if (
    !trace.rendered_observation ||
    typeof trace.rendered_observation !== 'object' ||
    Array.isArray(trace.rendered_observation)
  ) {
    throw new Error(`Trace ${index} rendered_observation must be an object.`);
  }
}

function validateProviderTraceMetadata(trace, index) {
  if (trace.provider_label !== null && typeof trace.provider_label !== 'string') {
    throw new Error(`Trace ${index} provider_label must be null or string.`);
  }
  if (trace.provider_model !== null && typeof trace.provider_model !== 'string') {
    throw new Error(`Trace ${index} provider_model must be null or string.`);
  }
  validateProviderUsage(trace.provider_usage, index);
}

function validateProviderUsage(usage, index) {
  if (usage === null) return;
  if (!usage || typeof usage !== 'object' || Array.isArray(usage)) {
    throw new Error(`Trace ${index} provider_usage must be null or object.`);
  }
  for (const [key, value] of Object.entries(usage)) {
    if (typeof value !== 'number' || value < 0) {
      throw new Error(`Trace ${index} provider_usage.${key} must be a nonnegative number.`);
    }
  }
}

function validateLegalOptions(trace, index) {
  if (!Array.isArray(trace.legal_options)) {
    throw new Error(`Trace ${index} legal_options must be an array.`);
  }
  const hasSelectedAction = trace.legal_options.some(
    (option) => option && typeof option === 'object' && !Array.isArray(option) && option.action_id === trace.selected_action_id,
  );
  if (!hasSelectedAction) {
    throw new Error(`Trace ${index} selected_action_id missing from legal_options.`);
  }
}

function matchesReplayReference(reference, replay) {
  if (!reference || typeof reference !== 'object' || Array.isArray(reference)) return false;
  return ['mode', 'seed', 'agent', 'players', 'turns'].every((field) => reference[field] === replay[field]);
}

function findTraceForAction(traces, action) {
  if (!action) return null;
  return traces.find((trace) => actionMatchesTrace(action, trace)) ?? null;
}

function findMatchingAction(actions, trace) {
  return actions.find((action) => actionMatchesTrace(action, trace));
}

function actionMatchesTrace(action, trace) {
  return (
    action.action_id === trace.selected_action_id &&
    action.player_id === trace.player_id &&
    action.turn === trace.turn
  );
}
