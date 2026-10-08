import { formatPlayerId } from '../replay/replayFormatters.js';
import ContextDrawer from './ContextDrawer.jsx';
import PlayerTableau from './PlayerTableau.jsx';
import styles from './GameTable.module.css';

function GameTable({
  table,
  inspectorMode = 'Game',
  gameTab = 'Event',
  selectedContext = null,
  onInspectorModeChange,
  onGameTabChange,
  onSelectContext,
}) {
  const resolvedSelectedContext = resolveSelectedContext(table, selectedContext);

  function handleSelectContext(selectedContext) {
    onSelectContext?.(selectedContext);
  }

  return (
    <section className={styles.gameTable} aria-label="Nuclear War table">
      <div className={styles.tableSurface}>
        <EventStrip table={table} />
        <div className={styles.playerGrid} aria-label="Player tableaus">
          {table.players.map((player) => (
            <PlayerTableau
              key={player.playerId}
              onSelect={handleSelectContext}
              player={player}
              selectedContext={resolvedSelectedContext}
            />
          ))}
        </div>
      </div>
      <ContextDrawer
        context={table.context}
        gameTab={gameTab}
        inspectorMode={inspectorMode}
        onGameTabChange={onGameTabChange}
        onInspectorModeChange={onInspectorModeChange}
        selectedContext={resolvedSelectedContext}
      />
    </section>
  );
}

function EventStrip({ table }) {
  const activeLabel = table.activePlayerId ? formatPlayerId(table.activePlayerId) : 'table';
  const warnings = table.context?.warnings ?? [];

  return (
    <header className={styles.eventStrip} role="group" aria-label="Current event">
      <div>
        <p className={styles.eyebrow}>Current event</p>
        <h2>{table.eventTitle}</h2>
      </div>
      <div className={styles.eventMeta} aria-label="Event metadata">
        <span>Event {table.eventIndex}</span>
        <span>Turn {table.turn}</span>
        <span>Active {activeLabel}</span>
        <span>{table.sourceLabel}</span>
        {warnings.length > 0 ? <span className={styles.warningPill}>Warning</span> : null}
      </div>
    </header>
  );
}

function resolveSelectedContext(table, selectedContext) {
  if (!selectedContext) return null;

  const player = table.players.find((item) => item.playerId === selectedContext.playerId);
  if (!player) return null;

  if (selectedContext.kind === 'player') {
    return { kind: 'player', playerId: player.playerId, player };
  }

  if (selectedContext.kind === 'queue') {
    const slot = player.queue.find((item) => item.index === selectedContext.index);
    if (!slot) return null;
    return { kind: 'queue', playerId: player.playerId, index: slot.index, player, slot };
  }

  return null;
}

export default GameTable;
