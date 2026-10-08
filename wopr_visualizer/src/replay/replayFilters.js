export const REPLAY_FILTERS = [
  { id: 'all', label: 'All events', eventTypes: null },
  {
    id: 'combat',
    label: 'Combat',
    eventTypes: ['launch_declared', 'target_declared', 'spinner_result', 'warhead_detonated', 'intercept_success'],
  },
  {
    id: 'population',
    label: 'Population',
    eventTypes: [
      'propaganda_effect',
      'secret_population_damaged',
      'secret_population_gained',
      'secret_population_removed',
      'secret_population_stolen',
      'warhead_detonated',
    ],
  },
  {
    id: 'warnings',
    label: 'Warnings',
    eventTypes: [],
  },
];

export function frameMatchesFilter(frame, filterId) {
  if (filterId === 'warnings') {
    return frame.warnings.length > 0;
  }
  const filter = REPLAY_FILTERS.find((item) => item.id === filterId);
  if (!filter || !filter.eventTypes || !frame.event) {
    return true;
  }
  return filter.eventTypes.includes(frame.event.event_type);
}
