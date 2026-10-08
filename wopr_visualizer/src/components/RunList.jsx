import { runRows } from '../replay/batchSummary.js';
import styles from './RunList.module.css';

function RunList({ summary, dirFiles, onSelectRun, selectedSeed }) {
  const rows = runRows(summary);
  const canResolve = dirFiles && dirFiles.size > 0;

  return (
    <div className={styles.runList}>
      <header className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Runs</p>
          <h2>{rows.length} runs in batch</h2>
        </div>
        {canResolve ? null : <span className={styles.hint}>Load the batch directory to open individual runs.</span>}
      </header>
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Seed</th>
              <th>Winner</th>
              <th>Turns</th>
              <th>Termination</th>
              <th>Elim</th>
              <th>Invalid</th>
              <th>Retries</th>
              <th>Traces</th>
              <th>Replay</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <RunRow
                canResolve={canResolve}
                dirFiles={dirFiles}
                isSelected={row.seed === selectedSeed}
                key={row.seed}
                onSelectRun={onSelectRun}
                row={row}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function RunRow({ row, canResolve, dirFiles, isSelected, onSelectRun }) {
  const replayFile = dirFiles?.get(row.replayPath) ?? null;
  const isClickable = canResolve && replayFile !== null;

  function handleClick() {
    if (!isClickable) return;
    onSelectRun(row);
  }

  function handleKey(event) {
    if (!isClickable) return;
    if (event.key === 'Enter') onSelectRun(row);
  }

  return (
    <tr
      aria-disabled={!isClickable}
      className={`${styles.row} ${isSelected ? styles.rowSelected : ''} ${isClickable ? styles.rowClickable : ''}`}
      onClick={handleClick}
      onKeyDown={handleKey}
      tabIndex={isClickable ? 0 : -1}
    >
      <td className={styles.mono}>{row.seed}</td>
      <td className={styles.winnerCell}>{formatWinner(row.winner)}</td>
      <td className={styles.mono}>{row.turns}</td>
      <td>{formatTermination(row.terminationReason)}</td>
      <td className={styles.mono}>{row.eliminations}</td>
      <td className={styles.mono}>{row.invalidActionCount}</td>
      <td className={styles.mono}>{row.retryCount}</td>
      <td className={styles.mono}>{row.traceCount}</td>
      <td className={styles.mono}>{row.replayPath}</td>
    </tr>
  );
}

function formatWinner(winner) {
  if (winner === null || winner === undefined) return 'No winner';
  return String(winner).replace('_', ' ');
}

function formatTermination(reason) {
  const text = String(reason || 'unknown').replaceAll('_', ' ');
  return `${text.charAt(0).toUpperCase()}${text.slice(1)}`;
}

export default RunList;
