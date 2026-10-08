import { formatEventType, formatPlayerId, formatSentenceLabel, formatValue } from './replayFormatters.js';

export function buildEventStory(frame) {
  if (!frame.event) {
    return {
      title: 'Initial state',
      body: 'Replay reconstruction starts from inferred player state.',
      actors: [],
      consequences: consequences(frame),
      warnings: warningMessages(frame),
    };
  }
  const event = frame.event;
  const eventType = event.event_type;
  return {
    title: formatSentenceLabel(eventType),
    body: storyBody(event),
    actors: event.player_id ? [event.player_id] : [],
    consequences: consequences(frame),
    warnings: warningMessages(frame),
  };
}

function storyBody(event) {
  const actor = playerLabel(event.player_id);
  const payload = event.payload ?? {};
  if (event.event_type === 'card_drawn') return `${actor} drew a card.`;
  if (event.event_type === 'cards_enqueued') {
    const count = Array.isArray(payload.cards) ? payload.cards.length : 0;
    return `${actor} added ${count} ${plural('card', count)} to the launch queue.`;
  }
  if (event.event_type === 'launch_declared') return `${actor} declared a launch.`;
  if (event.event_type === 'target_declared') return `${actor} targeted ${playerLabel(payload.target)}.`;
  if (event.event_type === 'warhead_detonated') {
    return `${actor} detonated a warhead against ${playerLabel(payload.target)} for ${formatValue(payload.yield)} population.`;
  }
  if (event.event_type === 'intercept_success') return `${actor} intercepted the attack.`;
  if (event.event_type === 'eliminated') return `${actor} was eliminated.`;
  if (event.event_type === 'peace_restored') return 'Peace was restored.';
  return `${actor} produced ${formatEventType(event.event_type)}.`;
}

function consequences(frame) {
  if (!frame.deltas || frame.deltas.length === 0) {
    return ['No derived state delta for this event.'];
  }
  return frame.deltas.map((delta) => (
    `${playerLabel(delta.playerId)} ${formatEventType(delta.field)}: ${formatValue(delta.before)} to ${formatValue(delta.after)}.`
  ));
}

function warningMessages(frame) {
  return (frame.warnings ?? []).map((warning) => warning.message);
}

function playerLabel(playerId) {
  if (!playerId) return 'The game';
  return titleCase(formatPlayerId(playerId));
}

function plural(word, count) {
  return count === 1 ? word : `${word}s`;
}

function titleCase(value) {
  return String(value)
    .split(' ')
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(' ');
}
