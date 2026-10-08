import { eventTone, formatSentenceLabel, formatPlayerId } from '../replay/replayFormatters.js';
import styles from './Transcript.module.css';

function Transcript({ events, selectedIndex, onSelectIndex }) {
  if (!events || events.length === 0) {
    return (
      <div className={styles.emptyPanel}>
        <p className={styles.label}>No transcript data in this replay.</p>
      </div>
    );
  }
  return (
    <div className={styles.list} role="log" aria-label="Event transcript">
      {events.map((event, index) => (
        <TranscriptRow
          event={event}
          index={index + 1}
          isActive={index + 1 === selectedIndex}
          key={`${index}-${event.event_type}`}
          onSelectIndex={onSelectIndex}
        />
      ))}
    </div>
  );
}

function TranscriptRow({ event, index, isActive, onSelectIndex }) {
  function handleClick() {
    onSelectIndex(index);
  }

  return (
    <button
      aria-current={isActive ? 'true' : undefined}
      className={`${styles.row} ${styles[`tone-${eventTone(event.event_type)}`] ?? ''} ${isActive ? styles.rowActive : ''}`}
      onClick={handleClick}
      type="button"
    >
      <span className={styles.index}>{String(index).padStart(3, '0')}</span>
      <span className={styles.body}>
        <span className={styles.type}>{formatSentenceLabel(event.event_type)}</span>
        {event.player_id ? (
          <span className={styles.actor}>{formatPlayerId(event.player_id)}</span>
        ) : null}
        {event.payload && Object.keys(event.payload).length > 0 ? (
          <span className={styles.payload}>{summarizePayload(event.payload)}</span>
        ) : null}
      </span>
    </button>
  );
}

function summarizePayload(payload) {
  const keys = Object.keys(payload);
  const preview = keys.slice(0, 2).map((key) => `${key}: ${shortValue(payload[key])}`).join(', ');
  return keys.length > 2 ? `${preview}, +${keys.length - 2}` : preview;
}

function shortValue(value) {
  if (value == null) return 'none';
  if (Array.isArray(value)) return value.length === 0 ? '[]' : `[${value.length}]`;
  if (typeof value === 'object') return '{...}';
  return String(value);
}

export default Transcript;
