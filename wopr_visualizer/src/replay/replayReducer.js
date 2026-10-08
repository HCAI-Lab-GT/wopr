import { findRelatedAction } from './actionLinking.js';
import { cloneState, reduceReplayEvent } from './eventReducer.js';
import { playerIdsForReplay, validateReplayPayload } from './replayValidation.js';
import { attachTraceFrames } from './traceArtifacts.js';

const DEFAULT_HAND_DRAW_TARGET = 10;
const DEFAULT_FACE_DOWN_CARDS = 2;

export function buildReplayFrames(payload, traceArtifact = null) {
  validateReplayPayload(payload);
  const initial = createInitialState(payload);
  const frames = [
    {
      eventIndex: 0,
      event: null,
      beforeState: null,
      afterState: cloneState(initial.state),
      deltas: [],
      relatedAction: null,
      warnings: initial.warnings,
    },
  ];
  let current = cloneState(initial.state);
  payload.events.forEach((event, index) => {
    const beforeState = cloneState(current);
    const result = reduceReplayEvent(current, event, index + 1);
    current = result.state;
    frames.push({
      eventIndex: index + 1,
      event,
      beforeState,
      afterState: cloneState(current),
      deltas: result.deltas,
      relatedAction: findRelatedAction(payload.actions, event),
      warnings: result.warnings,
    });
  });
  return attachTraceFrames(frames, traceArtifact);
}

export function warningCount(frames) {
  return frames.reduce((total, frame) => total + frame.warnings.length, 0);
}

function createInitialState(payload) {
  const playerIds = playerIdsForReplay(payload);
  const inferred = inferInitialPopulations(payload, playerIds);
  const handCount = initialHandCount(payload);
  const players = Object.fromEntries(
    playerIds.map((playerId) => [
      playerId,
      {
        playerId,
        population: inferred.populations[playerId] ?? 0,
        handCount,
        secretCount: 0,
        deterrentCount: 0,
        queue: [null, null],
        faceUp: null,
        alive: true,
        atWar: false,
      },
    ]),
  );
  return {
    state: {
      players,
      turn: 0,
      phase: 'initial',
      source: 'reconstructed from replay events',
    },
    warnings: inferred.warnings,
  };
}

function initialHandCount(payload) {
  const variant = payload.active_variant || {};
  const drawTarget = variant.hand_draw_target ?? DEFAULT_HAND_DRAW_TARGET;
  const faceDown = variant.initial_face_down_cards ?? DEFAULT_FACE_DOWN_CARDS;
  return Math.max(0, drawTarget - faceDown);
}

function inferInitialPopulations(payload, playerIds) {
  const populations = Object.fromEntries(
    playerIds.map((playerId) => [playerId, payload.final_populations[playerId] ?? 0]),
  );
  const warnings = [];
  for (const event of [...payload.events].reverse()) {
    reversePopulationEvent(populations, event, warnings);
  }
  return { populations, warnings };
}

function reversePopulationEvent(populations, event, warnings) {
  const amount = event.payload?.migrated ?? event.payload?.loss ?? event.payload?.yield;
  if (event.event_type === 'propaganda_effect' || event.event_type === 'secret_population_stolen') {
    const targetId = event.payload?.target;
    if (!Number.isFinite(amount) || !(event.player_id in populations) || !(targetId in populations)) return;
    populations[event.player_id] -= amount;
    populations[targetId] += amount;
    return;
  }
  if (event.event_type === 'warhead_detonated') {
    reverseLoss(populations, event.payload.target, amount);
    return;
  }
  if (event.event_type === 'secret_population_damaged' || event.event_type === 'secret_population_removed') {
    reverseLoss(populations, event.player_id, amount);
    return;
  }
  if (event.event_type === 'secret_population_gained') {
    warnings.push({
      eventIndex: 0,
      eventType: event.event_type,
      message: 'Initial population inference cannot reverse gain amount from this replay event.',
    });
  }
}

function reverseLoss(populations, playerId, amount) {
  if (!Number.isFinite(amount) || !(playerId in populations)) return;
  populations[playerId] += amount;
}
