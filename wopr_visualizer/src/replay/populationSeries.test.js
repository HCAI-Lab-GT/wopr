import { describe, expect, it } from 'vitest';
import {
  playerIdsFromFrames,
  populationSeries,
  seriesBounds,
} from './populationSeries.js';

function frame(eventIndex, turn, populations) {
  const players = Object.fromEntries(
    Object.entries(populations).map(([id, population]) => [id, { playerId: id, population }]),
  );
  return { eventIndex, afterState: { turn, players } };
}

const frames = [
  frame(0, 0, { player_0: 25, player_1: 25, player_2: 25 }),
  frame(1, 1, { player_0: 25, player_1: 25, player_2: 25 }),
  frame(2, 1, { player_0: 20, player_1: 25, player_2: 25 }),
  frame(3, 2, { player_0: 20, player_1: 18, player_2: 25 }),
  frame(4, 3, { player_0: 0, player_1: 18, player_2: 25 }),
];

describe('populationSeries', () => {
  it('samples the last frame of each turn boundary', () => {
    const { turns, series } = populationSeries(frames);
    expect(turns).toEqual([0, 1, 2, 3]);
    expect(series.player_0).toEqual([25, 20, 20, 0]);
    expect(series.player_1).toEqual([25, 25, 18, 18]);
    expect(series.player_2).toEqual([25, 25, 25, 25]);
  });

  it('uses the first frame turn as the initial sample', () => {
    const single = [frame(0, 1, { player_0: 30 })];
    const { turns, series } = populationSeries(single);
    expect(turns).toEqual([1]);
    expect(series.player_0).toEqual([30]);
  });

  it('returns empty series for empty frames', () => {
    const { turns, series } = populationSeries([], ['player_0']);
    expect(turns).toEqual([0]);
    expect(series.player_0).toEqual([]);
  });

  it('derives player ids from frames when omitted', () => {
    const { series } = populationSeries(frames);
    expect(Object.keys(series).sort()).toEqual(['player_0', 'player_1', 'player_2']);
  });
});

describe('playerIdsFromFrames', () => {
  it('sorts player ids', () => {
    expect(playerIdsFromFrames(frames)).toEqual(['player_0', 'player_1', 'player_2']);
  });

  it('returns empty when no frames', () => {
    expect(playerIdsFromFrames([])).toEqual([]);
  });
});

describe('seriesBounds', () => {
  it('returns the min and max across all players', () => {
    expect(seriesBounds({ player_0: [25, 20, 0], player_1: [25, 18] })).toEqual({ min: 0, max: 25 });
  });

  it('expands a flat range to avoid zero-height charts', () => {
    expect(seriesBounds({ player_0: [5, 5, 5] })).toEqual({ min: 5, max: 6 });
  });

  it('defaults to 0 when series is empty', () => {
    expect(seriesBounds({})).toEqual({ min: 0, max: 1 });
  });
});
