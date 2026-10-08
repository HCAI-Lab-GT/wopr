import styles from './CardZone.module.css';

function CardZone({ zone, zoneId, selected = false }) {
  const testId = zoneId ? `card-zone-${zoneId}` : 'card-zone';
  const className = [
    styles.cardZone,
    zone.changed ? styles.cardZoneChanged : '',
    selected ? styles.cardZoneSelected : '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div
      aria-label={zoneAccessibleName(zone, selected)}
      className={className}
      data-changed={zone.changed}
      data-selected={selected}
      data-testid={testId}
      role="group"
    >
      <span className={styles.label}>{zone.label}</span>
      <span className={styles.value}>{zone.value}</span>
    </div>
  );
}

function zoneAccessibleName(zone, selected) {
  const states = [];
  if (zone.changed) states.push('changed');
  if (selected) states.push('selected');
  return [zone.label, ...states].join(', ');
}

export default CardZone;
