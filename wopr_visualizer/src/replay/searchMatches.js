import { formatEventType } from './replayFormatters.js';

export function searchMatches(frame, query) {
  const normalized = normalizeQuery(query);
  if (!normalized) return true;
  const event = frame.event;
  if (!event) return false;
  if (formatEventType(event.event_type).includes(normalized)) return true;
  if (event.player_id && String(event.player_id).includes(normalized)) return true;
  if (containsInValue(event.payload, normalized)) return true;
  return false;
}

export function searchResultIndices(frames, query) {
  return frames.reduce((acc, frame, index) => {
    if (searchMatches(frame, query)) acc.push(index);
    return acc;
  }, []);
}

export function searchResultPosition(indices, selectedIndex) {
  if (indices.length === 0) return 0;
  const atOrAfter = indices.findIndex((index) => index >= selectedIndex);
  if (atOrAfter === -1) return indices.length;
  return atOrAfter + 1;
}

export function nextSearchIndex(indices, selectedIndex, cycle = true) {
  if (indices.length === 0) return selectedIndex;
  const next = indices.find((index) => index > selectedIndex);
  if (next !== undefined) return next;
  return cycle ? indices[0] : selectedIndex;
}

export function previousSearchIndex(indices, selectedIndex, cycle = true) {
  if (indices.length === 0) return selectedIndex;
  const previous = [...indices].reverse().find((index) => index < selectedIndex);
  if (previous !== undefined) return previous;
  return cycle ? indices[indices.length - 1] : selectedIndex;
}

function normalizeQuery(query) {
  return String(query ?? '').trim().toLowerCase();
}

function containsInValue(value, needle) {
  if (value == null) return false;
  if (typeof value === 'string') return value.toLowerCase().includes(needle);
  if (typeof value === 'number') return String(value).includes(needle);
  if (Array.isArray(value)) return value.some((item) => containsInValue(item, needle));
  if (typeof value === 'object') return Object.values(value).some((item) => containsInValue(item, needle));
  return false;
}
