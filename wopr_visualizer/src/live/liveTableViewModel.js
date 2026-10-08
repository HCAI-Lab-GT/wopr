import { formatPlayerId, formatSentenceLabel, formatValue } from '../replay/replayFormatters.js';

const LIVE_SOURCE_LABEL = 'Live local session';

export function buildLiveTableViewModel({ state, decision }) {
  const players = (state?.players ?? []).map((player) => buildPlayerModel(player, activePlayerId(decision)));
  const eventIndex = state?.state_version ?? decision?.state_version ?? 0;
  return {
    source: 'live',
    sourceLabel: formatSentenceLabel(state?.source_label ?? LIVE_SOURCE_LABEL),
    eventIndex,
    eventTitle: 'Live decision',
    turn: state?.turn ?? 0,
    activePlayerId: activePlayerId(decision),
    players,
    context: {
      frame: buildFrame(state, eventIndex),
      pendingDecision: decision ?? null,
      recentEvents: state?.recent_events ?? [],
      warnings: normalizeWarnings(state?.warnings),
    },
  };
}

function buildPlayerModel(player, activeId) {
  return {
    playerId: player.player_id,
    label: formatPlayerId(player.player_id),
    population: player.population,
    populationLabel: `${player.population}M`,
    populationChanged: false,
    alive: player.alive,
    aliveLabel: player.alive ? 'Alive' : 'Eliminated',
    aliveChanged: false,
    atWar: player.at_war,
    warLabel: player.at_war ? 'At war' : 'Peace',
    warChanged: false,
    active: activeId === player.player_id,
    changed: false,
    zones: {
      hand: zone('Hand', player.hand_count),
      secrets: zone('Secrets', player.secret_count),
      deterrents: zone('Deterrents', player.deterrent_count),
      faceUp: zone('Face up', player.face_up),
    },
    queue: (player.queue ?? []).map((cardId, index) => queueSlot(cardId, index)),
    deltas: [],
  };
}

function buildFrame(state, eventIndex) {
  return {
    event: null,
    eventIndex,
    afterState: {
      source: state?.source_label ?? LIVE_SOURCE_LABEL,
      turn: state?.turn ?? 0,
      phase: 'live',
      players: Object.fromEntries((state?.players ?? []).map((player) => [player.player_id, framePlayer(player)])),
    },
    deltas: [],
    relatedAction: null,
    warnings: normalizeWarnings(state?.warnings).map((message) => ({ message })),
  };
}

function framePlayer(player) {
  return {
    playerId: player.player_id,
    population: player.population,
    handCount: player.hand_count,
    secretCount: player.secret_count,
    deterrentCount: player.deterrent_count,
    faceUp: player.face_up,
    queue: player.queue ?? [],
    alive: player.alive,
    atWar: player.at_war,
  };
}

function activePlayerId(decision) {
  return decision?.pending ? decision.agent_id : null;
}

function zone(label, value) {
  return {
    label,
    value: formatValue(value),
    empty: value === null || value === undefined || value === 0,
    changed: false,
  };
}

function queueSlot(cardId, index) {
  return {
    index,
    label: cardId || `Slot ${index + 1}`,
    cardId,
    empty: !cardId,
    changed: false,
  };
}

function normalizeWarnings(warnings) {
  return (warnings ?? []).map((warning) => {
    if (typeof warning === 'string') return warning;
    return warning?.message ?? formatValue(warning);
  });
}
