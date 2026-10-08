import {
  agentMetricRows,
  agentOutcomeRows,
  averageTurns,
  batchMeta,
  providerTotals,
  terminationCounts,
  totals,
  winnerCounts,
} from '../replay/batchSummary.js';
import styles from './BatchSummary.module.css';

function BatchSummary({ summary }) {
  const meta = batchMeta(summary);
  const outcomes = agentOutcomeRows(summary);
  const metrics = agentMetricRows(summary);
  const winners = winnerCounts(summary);
  const terminations = terminationCounts(summary);
  const aggregateTotals = totals(summary);
  const providers = providerTotals(summary);
  const avgTurns = averageTurns(summary);

  return (
    <div className={styles.summary}>
      <header className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Batch summary</p>
          <h2>{meta.runs} runs, {meta.players} players, seeds {meta.seedStart}+</h2>
        </div>
        <span className={styles.tag}>{meta.mode}</span>
      </header>
      <div className={styles.grid}>
        <StatPanel label="Average turns">{avgTurns.toFixed(1)}</StatPanel>
        <StatPanel label="Total eliminations">{aggregateTotals.eliminations}</StatPanel>
        <StatPanel label="Decision traces">{aggregateTotals.traceCount}</StatPanel>
        <StatPanel label="Invalid actions">{aggregateTotals.invalidActionCount}</StatPanel>
        <StatPanel label="Retries">{aggregateTotals.retryCount}</StatPanel>
        <ProviderPanel providers={providers} />
      </div>
      <div className={styles.tables}>
        <OutcomeTable rows={outcomes} />
        <MetricTable rows={metrics} />
        <CountTable caption="Winners" rows={winners} valueKey="winner" />
        <CountTable caption="Termination reasons" rows={terminations} valueKey="reason" />
      </div>
    </div>
  );
}

function StatPanel({ label, children }) {
  return (
    <div className={styles.statPanel}>
      <p className={styles.label}>{label}</p>
      <p className={styles.statValue}>{children}</p>
    </div>
  );
}

function ProviderPanel({ providers }) {
  return (
    <div className={styles.statPanel}>
      <p className={styles.label}>Provider totals</p>
      <p className={styles.statValue}>
        {providers.latencyMs === null && providers.cost === null
          ? 'No provider data'
          : `${formatLatency(providers.latencyMs)} / ${formatCost(providers.cost)}`}
      </p>
    </div>
  );
}

function OutcomeTable({ rows }) {
  return (
    <div className={styles.tablePanel}>
      <p className={styles.label}>Agent outcomes</p>
      {rows.length === 0 ? (
        <p className={styles.empty}>No agent outcomes recorded.</p>
      ) : (
        <table className={styles.table}>
          <thead>
            <tr><th>Agent</th><th>Win</th><th>Loss</th><th>Draw</th></tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.agent}>
                <td>{row.agent}</td>
                <td className={styles.win}>{row.win}</td>
                <td className={styles.loss}>{row.loss}</td>
                <td>{row.draw}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function MetricTable({ rows }) {
  return (
    <div className={styles.tablePanel}>
      <p className={styles.label}>Agent decision metrics</p>
      {rows.length === 0 ? (
        <p className={styles.empty}>No decision metrics recorded.</p>
      ) : (
        <table className={styles.table}>
          <thead>
            <tr><th>Agent</th><th>Traces</th><th>Invalid</th><th>Rate</th><th>Retries</th><th>Rate</th></tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.agent}>
                <td>{row.agent}</td>
                <td>{row.traceCount}</td>
                <td>{row.invalidActionCount}</td>
                <td>{formatRate(row.invalidActionRate)}</td>
                <td>{row.retryCount}</td>
                <td>{formatRate(row.retryRate)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function CountTable({ caption, rows, valueKey }) {
  return (
    <div className={styles.tablePanel}>
      <p className={styles.label}>{caption}</p>
      {rows.length === 0 ? (
        <p className={styles.empty}>No {caption.toLowerCase()} recorded.</p>
      ) : (
        <table className={styles.table}>
          <thead>
            <tr><th>{formatHeader(valueKey)}</th><th>Count</th></tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row[valueKey]}>
                <td>{row[valueKey]}</td>
                <td>{row.count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

function formatRate(value) {
  return `${(value * 100).toFixed(0)}%`;
}

function formatLatency(latencyMs) {
  if (latencyMs === null || latencyMs === undefined) return 'N/A';
  return `${latencyMs} ms`;
}

function formatCost(cost) {
  if (cost === null || cost === undefined) return 'N/A';
  return `$${Number(cost).toFixed(4)}`;
}

function formatHeader(value) {
  const text = String(value).replaceAll('_', ' ');
  return `${text.charAt(0).toUpperCase()}${text.slice(1)}`;
}

export default BatchSummary;
