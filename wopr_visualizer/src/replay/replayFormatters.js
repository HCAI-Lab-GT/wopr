export function formatPlayerId(playerId) {
  return String(playerId).replace('_', ' ');
}

export function formatEventType(eventType) {
  return formatWords(eventType || 'initial_state').toLowerCase();
}

export function formatSentenceLabel(value) {
  const text = formatWords(value || 'initial_state').toLowerCase();
  return `${text.charAt(0).toUpperCase()}${text.slice(1)}`;
}

export function formatValue(value) {
  if (value === null || value === undefined) {
    return 'unknown';
  }
  if (Array.isArray(value)) {
    return value.filter(Boolean).join(', ') || 'empty';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

export function eventTone(eventType) {
  if (!eventType) {
    return 'neutral';
  }
  if (eventType.includes('detonated') || eventType.includes('eliminated')) {
    return 'danger';
  }
  if (eventType.includes('launch') || eventType.includes('target')) {
    return 'warning';
  }
  if (eventType.includes('intercept') || eventType.includes('peace')) {
    return 'stable';
  }
  return 'neutral';
}

function formatWords(value) {
  return String(value).replace(/([a-z0-9])([A-Z])/g, '$1 $2').replaceAll('_', ' ').trim();
}
