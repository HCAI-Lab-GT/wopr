import { formatSentenceLabel, formatValue } from '../replay/replayFormatters.js';
import CardZone from './CardZone.jsx';
import QueueLane from './QueueLane.jsx';
import styles from './PlayerTableau.module.css';

function PlayerTableau({ player, selectedContext = null, onSelect }) {
  const selected = selectedContext?.kind === 'player' && selectedContext.playerId === player.playerId;

  function handlePlayerSelect() {
    onSelect?.({ kind: 'player', playerId: player.playerId });
  }

  const className = [
    styles.playerTableau,
    player.active ? styles.playerTableauActive : '',
    player.changed ? styles.playerTableauChanged : '',
    selected ? styles.playerTableauSelected : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <article
      className={className}
      data-selected={selected}
      data-testid={`player-tableau-${player.playerId}`}
    >
      <header className={styles.header}>
        <div>
          <h3 className={styles.playerName}>{player.label}</h3>
          <div className={styles.statusRow}>
            <span
              aria-label={changedAccessibleName(player.aliveLabel, player.aliveChanged)}
              className={styles.statusTag}
              data-changed={player.aliveChanged}
              data-testid={`player-alive-${player.playerId}`}
            >
              {player.aliveLabel}
            </span>
            <span
              aria-label={changedAccessibleName(player.warLabel, player.warChanged)}
              className={styles.statusTag}
              data-changed={player.warChanged}
              data-testid={`player-war-${player.playerId}`}
            >
              {player.warLabel}
            </span>
          </div>
        </div>
        <div className={styles.headerControls}>
          <strong
            aria-label={changedAccessibleName(`population ${player.populationLabel}`, player.populationChanged)}
            className={styles.population}
            data-changed={player.populationChanged}
            data-testid={`player-population-${player.playerId}`}
          >
            {player.populationLabel}
          </strong>
          <button
            aria-pressed={selected}
            aria-label={`Select ${player.label}`}
            className={styles.selectButton}
            onClick={handlePlayerSelect}
            type="button"
          >
            Select
          </button>
        </div>
      </header>
      <div className={styles.zoneGrid}>
        {Object.entries(player.zones).map(([zoneId, zone]) => (
          <CardZone key={zoneId} zone={zone} zoneId={zoneId} />
        ))}
      </div>
      <QueueLane
        onSelect={onSelect}
        playerId={player.playerId}
        queue={player.queue}
        selectedContext={selectedContext}
      />
      {player.deltas.length > 0 ? (
        <div className={styles.deltaList} aria-label={`${player.playerId} state changes`}>
          {player.deltas.map((delta) => (
            <span className={styles.deltaItem} key={`${delta.field}-${delta.reason}`}>
              {formatSentenceLabel(delta.field)}: {formatValue(delta.before)} to {formatValue(delta.after)}
            </span>
          ))}
        </div>
      ) : null}
    </article>
  );
}

function changedAccessibleName(label, changed) {
  return changed ? `${label}, changed` : label;
}

export default PlayerTableau;
