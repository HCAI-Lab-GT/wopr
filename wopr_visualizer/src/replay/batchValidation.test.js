import { describe, expect, it } from 'vitest';
import {
  findSummaryFile,
  parseBatchSummaryJson,
  resolveRunFiles,
  validateBatchSummary,
} from './batchValidation.js';
import sampleSummary from '../data/batch_summary.json';

function summaryJson() {
  return JSON.stringify(sampleSummary);
}

describe('parseBatchSummaryJson', () => {
  it('parses the bundled fixture', () => {
    const payload = parseBatchSummaryJson(summaryJson());
    expect(payload.runs).toBe(3);
  });

  it('rejects invalid JSON', () => {
    expect(() => parseBatchSummaryJson('{')).toThrow('not valid JSON');
  });

  it('rejects a bare object missing required fields', () => {
    expect(() => parseBatchSummaryJson('{}')).toThrow('missing required field');
  });
});

describe('validateBatchSummary', () => {
  it('returns the payload when valid', () => {
    expect(validateBatchSummary(sampleSummary)).toBe(sampleSummary);
  });

  it('throws when results is not an array', () => {
    expect(() =>
      validateBatchSummary({ ...sampleSummary, results: {} }),
    ).toThrow('results must be an array');
  });
});

describe('findSummaryFile', () => {
  it('locates summary.json in a directory map', () => {
    const files = new Map([['seed-1.replay.json', {}], ['summary.json', { marker: true }]]);
    expect(findSummaryFile(files).marker).toBe(true);
  });

  it('returns null when absent', () => {
    expect(findSummaryFile(new Map([['other.json', {}]]))).toBeNull();
  });
});

describe('resolveRunFiles', () => {
  const result = sampleSummary.results[0];

  it('resolves replay and trace files by relative path', () => {
    const files = new Map([
      [result.replay_path, { name: 'replay' }],
      [result.trace_path, { name: 'traces' }],
    ]);
    const resolved = resolveRunFiles(result, files);
    expect(resolved.replay.name).toBe('replay');
    expect(resolved.traces.name).toBe('traces');
  });

  it('returns nulls when a path is missing', () => {
    const resolved = resolveRunFiles(result, new Map());
    expect(resolved.replay).toBeNull();
    expect(resolved.traces).toBeNull();
  });
});
