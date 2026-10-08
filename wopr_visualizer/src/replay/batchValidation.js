const REQUIRED_TOP_FIELDS = ['mode', 'players', 'seed_start', 'runs', 'results', 'summary', 'seat_config'];
const REQUIRED_SUMMARY_FIELDS = ['runs', 'average_turns'];

export function parseBatchSummaryJson(text) {
  let payload;
  try {
    payload = JSON.parse(text);
  } catch {
    throw new Error('Batch summary is not valid JSON.');
  }
  validateBatchSummary(payload);
  return payload;
}

export function validateBatchSummary(payload) {
  if (!payload || typeof payload !== 'object') {
    throw new Error('Batch summary must be a JSON object.');
  }
  for (const field of REQUIRED_TOP_FIELDS) {
    if (!(field in payload)) {
      throw new Error(`Batch summary is missing required field: ${field}.`);
    }
  }
  const summary = payload.summary;
  if (!summary || typeof summary !== 'object') {
    throw new Error('Batch summary.summary must be an object.');
  }
  for (const field of REQUIRED_SUMMARY_FIELDS) {
    if (!(field in summary)) {
      throw new Error(`Batch summary.summary is missing field: ${field}.`);
    }
  }
  if (!Array.isArray(payload.results)) {
    throw new Error('Batch summary.results must be an array.');
  }
  return payload;
}

export function findSummaryFile(dirFiles) {
  for (const [name, file] of dirFiles.entries()) {
    if (name === 'summary.json') return file;
  }
  return null;
}

export function resolveRunFiles(result, dirFiles) {
  if (!dirFiles || dirFiles.size === 0) return { replay: null, traces: null };
  return {
    replay: dirFiles.get(result.replay_path) ?? null,
    traces: dirFiles.get(result.trace_path) ?? null,
  };
}
