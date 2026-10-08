import { formatSentenceLabel, formatPlayerId, formatValue } from './replayFormatters.js';

export function buildReplayTableViewModel({ frame, conversationArtifacts, failureSnapshot }) {
  const eventTurn = frame.event?.turn ?? frame.afterState?.turn ?? 0;
  const activePlayerId = frame.event?.player_id ?? frame.relatedAction?.player_id ?? null;
  const playerDeltas = groupDeltasByPlayer(frame.deltas);
  return {
    source: 'replay',
    sourceLabel: formatSentenceLabel(frame.afterState?.source ?? 'reconstructed from replay events'),
    eventIndex: frame.eventIndex,
    eventTitle: formatSentenceLabel(frame.event?.event_type),
    turn: eventTurn,
    activePlayerId,
    players: Object.values(frame.afterState.players).map((player) =>
      buildPlayerModel(player, activePlayerId, playerDeltas.get(player.playerId) ?? []),
    ),
    context: {
      frame,
      relatedAction: frame.relatedAction,
      decisionTrace: frame.decisionTrace ?? null,
      pressMessages: pressMessagesForTurn(conversationArtifacts, eventTurn),
      failureSnapshot: failureForTurn(failureSnapshot, eventTurn),
      warnings: (frame.warnings ?? []).map((warning) => warning.message),
    },
  };
}

function buildPlayerModel(player, activePlayerId, deltas) {
  return {
    playerId: player.playerId,
    label: formatPlayerId(player.playerId),
    population: player.population,
    populationLabel: `${player.population}M`,
    populationChanged: changedField(deltas, 'population'),
    alive: player.alive,
    aliveLabel: player.alive ? 'Alive' : 'Eliminated',
    aliveChanged: changedField(deltas, 'alive'),
    atWar: player.atWar,
    warLabel: player.atWar ? 'At war' : 'Peace',
    warChanged: changedField(deltas, 'atWar'),
    active: activePlayerId === player.playerId,
    changed: deltas.length > 0,
    zones: {
      hand: zone('Hand', player.handCount, changedField(deltas, 'handCount')),
      secrets: zone('Secrets', player.secretCount, changedField(deltas, 'secretCount')),
      deterrents: zone('Deterrents', player.deterrentCount, changedField(deltas, 'deterrentCount')),
      faceUp: zone('Face up', player.faceUp, changedField(deltas, 'faceUp')),
    },
    queue: player.queue.map((cardId, index) => queueSlot(cardId, index, queueSlotChanged(deltas, index))),
    deltas,
  };
}

function zone(label, value, changed) {
  return {
    label,
    value: formatValue(value),
    empty: value === null || value === undefined || value === 0,
    changed,
  };
}

function queueSlot(cardId, index, changed) {
  return {
    index,
    label: cardId || `Slot ${index + 1}`,
    cardId,
    empty: !cardId,
    changed,
  };
}

function groupDeltasByPlayer(deltas) {
  const grouped = new Map();
  for (const delta of deltas ?? []) {
    const current = grouped.get(delta.playerId) ?? [];
    current.push(delta);
    grouped.set(delta.playerId, current);
  }
  return grouped;
}

function changedField(deltas, field) {
  return deltas.some((delta) => delta.field === field);
}

function queueSlotChanged(deltas, index) {
  return deltas.some((delta) => delta.field === 'queue' && delta.before?.[index] !== delta.after?.[index]);
}

function pressMessagesForTurn(conversationArtifacts, turn) {
  return (conversationArtifacts?.messages ?? []).filter((message) => message.turn === turn);
}

function failureForTurn(failureSnapshot, turn) {
  const failure = failureSnapshot?.decision_failure;
  if (!failure || failure.turn !== turn) return null;
  return failureSnapshot;
}
