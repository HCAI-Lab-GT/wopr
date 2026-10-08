const NO_CHANGE_EVENTS = new Set(['final_strike_executed', 'final_strike_targeted', 'intercept_success', 'secret_triggered', 'secret_turns_lost', 'spinner_result', 'target_declared', 'turn_skipped']);

export function reduceReplayEvent(state, event, eventIndex) {
  const next = cloneState(state);
  const deltas = [];
  const warnings = [];
  const handler = EVENT_HANDLERS[event.event_type];
  if (handler) {
    handler(next, event, deltas, warnings, eventIndex);
  } else if (!NO_CHANGE_EVENTS.has(event.event_type)) {
    warnings.push(warning(eventIndex, event, 'No reducer handler for this event.'));
  }
  next.turn = event.turn || next.turn;
  return { state: next, deltas, warnings };
}

export function cloneState(state) {
  return structuredClone(state);
}

const EVENT_HANDLERS = {
  card_drawn(state, event, deltas) {
    changePlayer(state, event.player_id, 'handCount', 1, deltas, 'card drawn');
  },
  secret_queued(state, event, deltas) {
    changePlayer(state, event.player_id, 'handCount', -1, deltas, 'secret routed');
    changePlayer(state, event.player_id, 'secretCount', 1, deltas, 'secret queued');
  },
  cards_enqueued(state, event, deltas) {
    const cards = event.payload?.cards || event.payload?.card_ids || [];
    const player = state.players[event.player_id];
    if (!player) return;
    const beforeQueue = [...player.queue];
    for (const card of cards) {
      const slot = player.queue.findIndex((entry) => entry === null);
      if (slot >= 0) player.queue[slot] = card;
    }
    addDelta(deltas, event.player_id, 'queue', beforeQueue, player.queue, 'cards enqueued');
    changePlayer(state, event.player_id, 'handCount', -cards.length, deltas, 'cards enqueued');
  },
  delivery_ready: revealCard,
  propaganda_ready: revealCard,
  warhead_discarded: resolveCard,
  warhead_loaded: revealCard,
  card_resolved: resolveCard,
  propaganda_effect(state, event, deltas) {
    movePopulation(state, event.player_id, event.payload?.target, event.payload?.migrated, deltas, 'propaganda effect');
    setPlayerField(state, event.player_id, 'faceUp', null, deltas, 'propaganda resolved');
  },
  secret_population_stolen(state, event, deltas) {
    movePopulation(state, event.player_id, event.payload?.target, event.payload?.migrated, deltas, 'secret population stolen');
    setPlayerField(state, event.player_id, 'faceUp', null, deltas, 'secret resolved');
  },
  secret_population_damaged: reduceSecretPopulationLoss,
  secret_population_removed: reduceSecretPopulationLoss,
  secret_population_gained(state, event, deltas, warnings, eventIndex) {
    warnings.push(warning(eventIndex, event, 'Population gain event does not expose gained amount.'));
    setPlayerField(state, event.player_id, 'faceUp', null, deltas, 'secret resolved');
  },
  launch_declared(state, event, deltas) {
    const target = event.payload?.target_id || event.payload?.target;
    setWarState(state, event.player_id, true, deltas, 'launch declared');
    setWarState(state, target, true, deltas, 'launch target');
    setPlayerField(state, event.player_id, 'faceUp', event.card_id, deltas, 'launch declared');
  },
  warhead_detonated(state, event, deltas) {
    losePopulation(state, event.payload?.target, event.payload?.loss ?? event.payload?.yield, deltas, 'warhead detonated');
    setPlayerField(state, event.player_id, 'faceUp', null, deltas, 'warhead detonated');
  },
  player_eliminated(state, event, deltas) {
    setPlayerField(state, event.player_id, 'population', 0, deltas, 'player eliminated');
    setPlayerField(state, event.player_id, 'alive', false, deltas, 'player eliminated');
  },
  peace_restored(state, event, deltas) {
    for (const playerId of Object.keys(state.players)) {
      setWarState(state, playerId, false, deltas, 'peace restored');
    }
  },
};

function reduceSecretPopulationLoss(state, event, deltas) {
  losePopulation(state, event.player_id, event.payload?.loss, deltas, event.event_type.replaceAll('_', ' '));
  setPlayerField(state, event.player_id, 'faceUp', null, deltas, 'secret resolved');
}

function revealCard(state, event, deltas) {
  consumeQueuedCard(state, event, deltas);
  setPlayerField(state, event.player_id, 'faceUp', event.card_id, deltas, 'card visible');
}

function resolveCard(state, event, deltas) {
  consumeQueuedCard(state, event, deltas);
  setPlayerField(state, event.player_id, 'faceUp', null, deltas, 'card resolved');
}

function consumeQueuedCard(state, event, deltas) {
  const player = state.players[event.player_id];
  if (!player) return;
  const beforeQueue = [...player.queue];
  const match = player.queue.findIndex((card) => card === event.card_id);
  if (match >= 0) {
    player.queue[match] = null;
  } else if (player.queue[0] !== null) {
    player.queue.shift();
    player.queue.push(null);
  }
  addDelta(deltas, event.player_id, 'queue', beforeQueue, player.queue, 'queue advanced');
}

function movePopulation(state, actorId, targetId, amount, deltas, reason) {
  if (!Number.isFinite(amount)) return;
  changePlayer(state, actorId, 'population', amount, deltas, reason);
  changePlayer(state, targetId, 'population', -amount, deltas, reason);
}

function losePopulation(state, playerId, amount, deltas, reason) {
  if (!Number.isFinite(amount)) return;
  changePlayer(state, playerId, 'population', -amount, deltas, reason);
}

function changePlayer(state, playerId, field, amount, deltas, reason) {
  const player = state.players[playerId];
  if (!player) return;
  const before = player[field];
  const after = Math.max(0, before + amount);
  player[field] = after;
  addDelta(deltas, playerId, field, before, after, reason);
}

function setWarState(state, playerId, atWar, deltas, reason) {
  setPlayerField(state, playerId, 'atWar', atWar, deltas, reason);
}

function setPlayerField(state, playerId, field, value, deltas, reason) {
  const player = state.players[playerId];
  if (!player) return;
  const before = player[field];
  player[field] = value;
  addDelta(deltas, playerId, field, before, value, reason);
}

function addDelta(deltas, playerId, field, before, after, reason) {
  if (JSON.stringify(before) === JSON.stringify(after)) return;
  deltas.push({ playerId, field, before, after, reason });
}

function warning(eventIndex, event, message) {
  return { eventIndex, eventType: event.event_type, message };
}
