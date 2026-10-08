import { formatPlayerId } from './replayFormatters.js';

const SUPPORTED_SCHEMA_VERSIONS = new Set([1]);
const PRESS_MODES = new Set([
  'press_light',
  'multi_turn_public',
  'full_press',
]);
const REQUIRED_FIELDS = ['schema_version', 'press_mode', 'replay', 'messages'];

export function parsePressArtifactJson(text, replay) {
  let payload;
  try {
    payload = JSON.parse(text);
  } catch {
    throw new Error('Press artifact is not valid JSON.');
  }
  validatePressArtifact(payload, replay);
  return payload;
}

export function validatePressArtifact(payload, replay) {
  if (!isObject(payload)) throw new Error('Press artifact must be an object.');
  for (const field of REQUIRED_FIELDS) {
    if (!(field in payload)) {
      throw new Error(`Press artifact missing field: ${field}`);
    }
  }
  const extra = Object.keys(payload).filter(
    (key) => !REQUIRED_FIELDS.includes(key),
  );
  if (extra.length) throw new Error('Press artifact fields are invalid.');
  if (!SUPPORTED_SCHEMA_VERSIONS.has(payload.schema_version)) {
    throw new Error('Press artifact schema_version is invalid.');
  }
  if (!PRESS_MODES.has(payload.press_mode)) {
    throw new Error('Press artifact press_mode is invalid.');
  }
  if (!sameReplay(payload.replay, replay)) {
    throw new Error('Press artifact replay reference does not match replay.');
  }
  if (!Array.isArray(payload.messages)) {
    throw new Error('Press artifact messages must be a list.');
  }
}

export function normalizePressArtifacts(payload) {
  const messages = Array.isArray(payload?.messages) ? payload.messages : [];
  if (messages.length === 0) {
    return { messages: [], source: 'none' };
  }
  return {
    messages: messages.map((message, index) => normalizeMessage(message, index)),
    source: 'press',
  };
}

function normalizeMessage(message, index) {
  return {
    id: message.message_id ?? `press-${index}`,
    turn: message.turn,
    speaker: message.speaker,
    speakerLabel: participantLabel(message.speaker),
    audience: message.audience,
    audienceLabel: participantLabel(message.audience),
    text: message.text,
    visibility: message.visibility ?? 'public',
    recipient: message.recipient ?? null,
    recipientLabel: participantLabel(message.recipient),
    commitment: message.commitment ?? null,
  };
}

function participantLabel(value) {
  if (value === 'public') return 'Public';
  if (!value) return 'Unknown';
  return titleCase(formatPlayerId(value));
}

function titleCase(value) {
  return String(value)
    .split(' ')
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(' ');
}

function sameReplay(left, right) {
  return (
    isObject(left) &&
    isObject(right) &&
    left.mode === right.mode &&
    left.seed === right.seed &&
    left.agent === right.agent &&
    left.players === right.players &&
    left.turns === right.turns
  );
}

function isObject(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
