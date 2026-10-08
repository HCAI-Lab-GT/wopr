import styles from './QueueLane.module.css';

function QueueLane({ playerId, queue, selectedContext = null, onSelect }) {
  return (
    <div className={styles.queueLane} aria-label={`${playerId} queue lane`}>
      {queue.map((slot) => (
        <QueueSlot
          key={`${playerId}-queue-${slot.index}`}
          onSelect={onSelect}
          playerId={playerId}
          selected={isSelectedQueueSlot(selectedContext, playerId, slot.index)}
          slot={slot}
        />
      ))}
    </div>
  );
}

function QueueSlot({ playerId, slot, selected, onSelect }) {
  function handleSlotClick(event) {
    event.stopPropagation();
    onSelect?.({ kind: 'queue', playerId, index: slot.index });
  }

  const className = [
    styles.queueSlot,
    slot.empty ? styles.queueSlotEmpty : '',
    slot.changed ? styles.queueSlotChanged : '',
    selected ? styles.queueSlotSelected : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      aria-label={slotAccessibleName(slot, selected)}
      aria-pressed={selected}
      className={className}
      data-changed={slot.changed}
      data-empty={slot.empty}
      data-selected={selected}
      data-testid={`queue-slot-${playerId}-${slot.index}`}
      onClick={handleSlotClick}
      type="button"
    >
      {slot.label}
    </button>
  );
}

function isSelectedQueueSlot(selectedContext, playerId, index) {
  return selectedContext?.kind === 'queue' && selectedContext.playerId === playerId && selectedContext.index === index;
}

function slotAccessibleName(slot, selected) {
  const states = [];
  if (slot.empty) states.push('empty');
  if (slot.changed) states.push('changed');
  if (selected) states.push('selected');
  return [slot.label, ...states].join(', ');
}

export default QueueLane;
