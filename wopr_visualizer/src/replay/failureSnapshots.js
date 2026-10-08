const SECRET_KEYS = new Set(['api_key', 'authorization', 'bearer', 'token']);

export function parseFailureSnapshotJson(text) {
  let payload;
  try {
    payload = JSON.parse(text);
  } catch (error) {
    throw new Error(`Failure snapshot is not valid JSON: ${error.message}`, { cause: error });
  }
  validateSnapshot(payload);
  return payload;
}

function validateSnapshot(payload) {
  if (!isRecord(payload)) {
    throw new Error('Failure snapshot must be a JSON object.');
  }
  rejectSecretKeys(payload);
  const failure = decisionFailure(payload);
  if (!isRecord(failure.agent_identity)) {
    throw new Error('Failure snapshot decision_failure missing agent_identity.');
  }
  if (!Array.isArray(failure.legal_options)) {
    throw new Error('Failure snapshot decision_failure legal_options must be an array.');
  }
}

function decisionFailure(payload) {
  const failure = payload.decision_failure ?? payload;
  if (!isRecord(failure)) {
    throw new Error('Failure snapshot decision_failure must be a JSON object.');
  }
  return failure;
}

function rejectSecretKeys(value) {
  if (Array.isArray(value)) {
    value.forEach(rejectSecretKeys);
    return;
  }
  if (!isRecord(value)) return;
  for (const [key, item] of Object.entries(value)) {
    if (SECRET_KEYS.has(key.toLowerCase())) {
      throw new Error(`Failure snapshot contains secret-shaped key: ${key}`);
    }
    rejectSecretKeys(item);
  }
}

function isRecord(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}
