import { describe, expect, it } from 'vitest';
import {
  nextSearchIndex,
  previousSearchIndex,
  searchMatches,
  searchResultIndices,
  searchResultPosition,
} from './searchMatches.js';

function frame(eventIndex, event) {
  return { eventIndex, event, warnings: [] };
}

describe('searchMatches', () => {
  it('returns true for empty query', () => {
    expect(searchMatches(frame(1, { event_type: 'launch_declared' }), '')).toBe(true);
    expect(searchMatches(frame(1, { event_type: 'launch_declared' }), '   ')).toBe(true);
  });

  it('matches against the formatted event type', () => {
    expect(searchMatches(frame(1, { event_type: 'warhead_detonated' }), 'warhead')).toBe(true);
    expect(searchMatches(frame(1, { event_type: 'warhead_detonated' }), 'detonated')).toBe(true);
    expect(searchMatches(frame(1, { event_type: 'warhead_detonated' }), 'intercept')).toBe(false);
  });

  it('matches against player_id', () => {
    expect(searchMatches(frame(1, { event_type: 'x', player_id: 'player_2' }), 'player_2')).toBe(true);
    expect(searchMatches(frame(1, { event_type: 'x', player_id: 'player_2' }), '2')).toBe(true);
  });

  it('matches against payload values including nested objects and arrays', () => {
    expect(
      searchMatches(frame(1, { event_type: 'x', payload: { cards: ['nw_base_abc'] } }), 'abc'),
    ).toBe(true);
    expect(
      searchMatches(frame(1, { event_type: 'x', payload: { target: 'player_1' } }), 'player_1'),
    ).toBe(true);
  });

  it('is case-insensitive', () => {
    expect(searchMatches(frame(1, { event_type: 'launch_declared' }), 'LAUNCH')).toBe(true);
  });

  it('returns false for the synthetic initial state frame', () => {
    expect(searchMatches(frame(0, null), 'launch')).toBe(false);
  });
});

describe('searchResultIndices', () => {
  const frames = [
    frame(0, null),
    frame(1, { event_type: 'launch_declared', player_id: 'player_0' }),
    frame(2, { event_type: 'warhead_detonated', player_id: 'player_1' }),
    frame(3, { event_type: 'launch_declared', player_id: 'player_2' }),
  ];

  it('collects all matching indices', () => {
    expect(searchResultIndices(frames, 'launch')).toEqual([1, 3]);
  });

  it('returns every frame for empty query', () => {
    expect(searchResultIndices(frames, '')).toEqual([0, 1, 2, 3]);
  });
});

describe('searchResultPosition', () => {
  const indices = [1, 3, 5];

  it('returns 1-based position at or after the selection', () => {
    expect(searchResultPosition(indices, 0)).toBe(1);
    expect(searchResultPosition(indices, 1)).toBe(1);
    expect(searchResultPosition(indices, 2)).toBe(2);
    expect(searchResultPosition(indices, 5)).toBe(3);
  });

  it('returns count when selection is past the last match', () => {
    expect(searchResultPosition(indices, 7)).toBe(3);
  });

  it('returns 0 for no matches', () => {
    expect(searchResultPosition([], 4)).toBe(0);
  });
});

describe('nextSearchIndex / previousSearchIndex', () => {
  const indices = [1, 3, 5];

  it('next cycles forward and wraps', () => {
    expect(nextSearchIndex(indices, 0)).toBe(1);
    expect(nextSearchIndex(indices, 1)).toBe(3);
    expect(nextSearchIndex(indices, 5)).toBe(1);
  });

  it('previous cycles backward and wraps', () => {
    expect(previousSearchIndex(indices, 5)).toBe(3);
    expect(previousSearchIndex(indices, 3)).toBe(1);
    expect(previousSearchIndex(indices, 1)).toBe(5);
  });

  it('returns selection unchanged when no matches and cycle disabled', () => {
    expect(nextSearchIndex([], 4)).toBe(4);
    expect(previousSearchIndex([], 4)).toBe(4);
  });
});
