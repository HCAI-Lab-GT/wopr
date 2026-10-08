const OUTCOME_KEYS = ['win', 'loss', 'draw'];

export function batchMeta(summary) {
  return {
    mode: summary.mode,
    runs: summary.runs,
    players: summary.players,
    seedStart: summary.seed_start,
    maxTurns: summary.max_turns,
    seatConfig: summary.seat_config ?? {},
  };
}

export function agentOutcomeRows(summary) {
  const outcomes = summary.summary?.agent_outcomes ?? {};
  return Object.entries(outcomes)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([agent, counts]) => ({
      agent,
      win: counts.win ?? 0,
      loss: counts.loss ?? 0,
      draw: counts.draw ?? 0,
      total: OUTCOME_KEYS.reduce((sum, key) => sum + (counts[key] ?? 0), 0),
    }));
}

export function agentMetricRows(summary) {
  const metrics = summary.summary?.agent_decision_metrics ?? {};
  return Object.entries(metrics)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([agent, values]) => ({
      agent,
      traceCount: values.trace_count ?? 0,
      invalidActionCount: values.invalid_action_count ?? 0,
      invalidActionRate: values.invalid_action_rate ?? 0,
      retryCount: values.retry_count ?? 0,
      retryRate: values.retry_rate ?? 0,
    }));
}

export function winnerCounts(summary) {
  const counts = summary.summary?.winner_counts ?? {};
  return Object.entries(counts)
    .map(([winner, count]) => ({ winner, count }))
    .sort((a, b) => b.count - a.count);
}

export function terminationCounts(summary) {
  const counts = summary.summary?.termination_counts ?? {};
  return Object.entries(counts)
    .map(([reason, count]) => ({ reason, count }))
    .sort((a, b) => b.count - a.count);
}

export function providerTotals(summary) {
  const block = summary.summary ?? {};
  return {
    latencyMs: providerValue(block, 'total_provider_latency_ms'),
    cost: providerValue(block, 'total_provider_cost'),
  };
}

export function runRows(summary) {
  return (summary.results ?? []).map((result) => ({
    seed: result.seed,
    winner: result.winner,
    turns: result.turns,
    terminationReason: result.termination_reason,
    eliminations: result.elimation_order?.length ?? result.elimination_order?.length ?? 0,
    invalidActionCount: result.invalid_action_count ?? 0,
    retryCount: result.retry_count ?? 0,
    traceCount: result.trace_count ?? 0,
    replayPath: result.replay_path,
    tracePath: result.trace_path,
    outcomes: result.win_loss ?? {},
  }));
}

export function averageTurns(summary) {
  const value = summary.summary?.average_turns;
  return typeof value === 'number' ? value : 0;
}

export function totals(summary) {
  const block = summary.summary ?? {};
  return {
    eliminations: block.total_eliminations ?? 0,
    invalidActionCount: block.total_invalid_action_count ?? 0,
    retryCount: block.total_retry_count ?? 0,
    traceCount: block.total_trace_count ?? 0,
  };
}

function providerValue(block, key) {
  const value = block[key];
  if (value === null || value === undefined) return null;
  return value;
}
