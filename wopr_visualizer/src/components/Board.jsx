import styles from './Board.module.css';
import PlayerStrip from './PlayerStrip.jsx';

function Board({ frame }) {
  const state = frame.afterState;
  const activePlayer = frame.event?.player_id || frame.relatedAction?.player_id || null;
  return (
    <section className={styles.board} aria-label="Reconstructed board">
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Board</p>
          <h2>Reconstructed state</h2>
        </div>
        <span className={styles.tag}>{state.source}</span>
      </div>
      <div className={styles.playerGrid}>
        {Object.values(state.players).map((player) => (
          <PlayerStrip
            key={player.playerId}
            player={player}
            active={activePlayer === player.playerId}
            deltas={frame.deltas.filter((delta) => delta.playerId === player.playerId)}
          />
        ))}
      </div>
    </section>
  );
}

export default Board;
