import { describe, expect, it } from 'vitest';
import sampleSummary from '../data/batch_summary.json';
import {
  agentMetricRows,
  agentOutcomeRows,
  averageTurns,
  batchMeta,
  providerTotals,
  runRows,
  terminationCounts,
  totals,
  winnerCounts,
} from './batchSummary.js';

describe('batchSummary selectors (real fixture)', () => {
  it('batchMeta reads top-level config fields', () => {
    const meta = batchMeta(sampleSummary);
    expect(meta.runs).toBe(3);
    expect(meta.players).toBe(4);
    expect(meta.seedStart).toBe(101);
    expect(meta.seatConfig).toHaveProperty('player_0', 'heuristic');
  });

  it('agentOutcomeRows returns one row per agent with win/loss/draw and a total', () => {
    const rows = agentOutcomeRows(sampleSummary);
    expect(rows.length).toBeGreaterThan(0);
    const heuristic = rows.find((row) => row.agent === 'heuristic');
    expect(heuristic.total).toBe(heuristic.win + heuristic.loss + heuristic.draw);
  });

  it('agentMetricRows returns rate fields as numbers', () => {
    const rows = agentMetricRows(sampleSummary);
    expect(rows.length).toBeGreaterThan(0);
    rows.forEach((row) => {
      expect(typeof row.invalidActionRate).toBe('number');
      expect(typeof row.retryRate).toBe('number');
    });
  });

  it('winnerCounts sorts by count descending', () => {
    const rows = winnerCounts(sampleSummary);
    expect(rows.length).toBeGreaterThan(0);
    for (let i = 1; i < rows.length; i += 1) {
      expect(rows[i - 1].count).toBeGreaterThanOrEqual(rows[i].count);
    }
  });

  it('terminationCounts returns reason/count pairs', () => {
    const rows = terminationCounts(sampleSummary);
    expect(rows.length).toBeGreaterThan(0);
    expect(rows.every((row) => typeof row.reason === 'string')).toBe(true);
  });

  it('providerTotals returns nulls when provider data absent', () => {
    const totalsRow = providerTotals(sampleSummary);
    expect(totalsRow.latencyMs).toBeNull();
    expect(totalsRow.cost).toBeNull();
  });

  it('runRows maps every result with replay and trace paths', () => {
    const rows = runRows(sampleSummary);
    expect(rows).toHaveLength(sampleSummary.results.length);
    expect(rows[0].replayPath).toMatch(/^seed-\d+\.replay\.json$/);
    expect(rows[0].tracePath).toMatch(/^seed-\d+\.replay\.traces\.json$/);
  });

  it('averageTurns and totals read aggregate fields', () => {
    expect(averageTurns(sampleSummary)).toBeGreaterThan(0);
    const block = totals(sampleSummary);
    expect(block.traceCount).toBe(0);
    expect(block.eliminations).toBeGreaterThan(0);
  });
});

describe('batchSummary selectors (missing fields)', () => {
  const empty = {};

  it('returns empty arrays and zeros for a bare object', () => {
    expect(agentOutcomeRows(empty)).toEqual([]);
    expect(agentMetricRows(empty)).toEqual([]);
    expect(winnerCounts(empty)).toEqual([]);
    expect(terminationCounts(empty)).toEqual([]);
    expect(runRows(empty)).toEqual([]);
    expect(averageTurns(empty)).toBe(0);
    expect(totals(empty).traceCount).toBe(0);
    expect(providerTotals(empty).latencyMs).toBeNull();
  });
});
