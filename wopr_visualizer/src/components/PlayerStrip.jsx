import { formatPlayerId, formatSentenceLabel, formatValue } from '../replay/replayFormatters.js';
import styles from './PlayerStrip.module.css';

function PlayerStrip({ player, active, deltas }) {
  const className = [
    styles.playerStrip,
    active ? styles.playerStripActive : '',
    deltas.length > 0 ? styles.playerStripChanged : '',
  ]
    .filter(Boolean)
    .join(' ');
  return (
    <article className={className}>
      <div className={styles.playerHead}>
        <div>
          <h3 className={styles.playerName}>{formatPlayerId(player.playerId)}</h3>
          <div className={styles.tagRow}>
            <span className={styles.tag}>{player.alive ? 'Alive' : 'Eliminated'}</span>
            <span className={styles.tag}>{player.atWar ? 'At war' : 'Peace'}</span>
          </div>
        </div>
        <strong>{player.population}M</strong>
      </div>
      <div className={styles.metricGrid}>
        <Metric label="Hand" value={player.handCount} />
        <Metric label="Secrets" value={player.secretCount} />
        <Metric label="Deterrents" value={player.deterrentCount} />
        <Metric label="Face up" value={formatValue(player.faceUp)} />
      </div>
      <div className={styles.queueRow}>
        {player.queue.map((cardId, index) => (
          <span className={styles.queueSlot} key={`${player.playerId}-queue-${index}`}>
            {cardId || `Slot ${index + 1}`}
          </span>
        ))}
      </div>
      {deltas.length > 0 ? (
        <div className={styles.deltaList} aria-label={`${player.playerId} state changes`}>
          {deltas.map((delta) => (
            <span className={styles.deltaItem} key={`${delta.field}-${delta.reason}`}>
              {formatSentenceLabel(delta.field)}: {formatValue(delta.before)} to {formatValue(delta.after)}
            </span>
          ))}
        </div>
      ) : null}
    </article>
  );
}

function Metric({ label, value }) {
  return (
    <div className={styles.metric}>
      <div className={styles.metricLabel}>{label}</div>
      <div className={styles.metricValue}>{value}</div>
    </div>
  );
}

export default PlayerStrip;
