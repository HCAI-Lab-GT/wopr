const REQUIRED_REPLAY_FIELDS = [
  'mode',
  'seed',
  'agent',
  'players',
  'turns',
  'winner',
  'termination_reason',
  'final_populations',
  'actions',
  'events',
];

export function parseReplayJson(text) {
  let payload;
  try {
    payload = JSON.parse(text);
  } catch (error) {
    throw new Error(`Replay file is not valid JSON: ${error.message}`, { cause: error });
  }
  return validateReplayPayload(payload);
}

export function validateReplayPayload(payload) {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    throw new Error('Replay payload must be a JSON object.');
  }
  for (const field of REQUIRED_REPLAY_FIELDS) {
    if (!(field in payload)) {
      throw new Error(`Replay payload missing required field: ${field}`);
    }
  }
  if (!Number.isInteger(payload.players) || payload.players < 2) {
    throw new Error('Replay players must be an integer of at least 2.');
  }
  if (!Array.isArray(payload.actions) || payload.actions.length === 0) {
    throw new Error('Replay actions must be a non-empty array.');
  }
  if (!Array.isArray(payload.events) || payload.events.length === 0) {
    throw new Error('Replay events must be a non-empty array.');
  }
  if (!isObject(payload.final_populations)) {
    throw new Error('Replay final_populations must be an object.');
  }
  return payload;
}

export function playerIdsForReplay(payload) {
  const populationIds = Object.keys(payload.final_populations || {});
  if (populationIds.length > 0) {
    return populationIds;
  }
  return Array.from({ length: payload.players }, (_, index) => `player_${index}`);
}

function isObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}
