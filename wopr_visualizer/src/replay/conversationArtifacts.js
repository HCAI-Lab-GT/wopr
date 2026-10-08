import { formatPlayerId } from './replayFormatters.js';

export function normalizeConversationArtifacts(payload) {
  const press = Array.isArray(payload?.press) ? payload.press : [];
  if (press.length === 0) {
    return { messages: [], source: 'none' };
  }
  return {
    messages: press.map((message, index) => normalizeMessage(message, index)),
    source: 'press',
  };
}

function normalizeMessage(message, index) {
  return {
    id: message.id ?? `press-${index}`,
    turn: message.turn,
    speaker: message.speaker,
    speakerLabel: participantLabel(message.speaker),
    audience: message.audience,
    audienceLabel: participantLabel(message.audience),
    text: message.text,
    visibility: message.visibility ?? 'public',
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
