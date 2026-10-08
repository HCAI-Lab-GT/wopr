export function populationSeries(frames, playerIds) {
  const ids = playerIds ?? playerIdsFromFrames(frames);
  if (frames.length === 0 || ids.length === 0) {
    return { turns: [0], series: Object.fromEntries(ids.map((id) => [id, []])) };
  }

  const series = Object.fromEntries(ids.map((id) => [id, []]));
  const turns = [];
  let lastTurn = null;
  let pending = null;

  const commit = (turn, players) => {
    turns.push(turn);
    ids.forEach((id) => {
      series[id].push(Number(players?.[id]?.population ?? 0));
    });
  };

  frames.forEach((frame) => {
    const turn = frame.afterState?.turn ?? 0;
    const players = frame.afterState?.players ?? {};
    if (turn !== lastTurn) {
      if (pending !== null) commit(pending.turn, pending.players);
      pending = { turn, players };
      lastTurn = turn;
    } else {
      pending = { turn, players };
    }
  });

  if (pending !== null) commit(pending.turn, pending.players);
  else { turns.push(0); ids.forEach((id) => series[id].push(0)); }

  return { turns, series };
}

export function playerIdsFromFrames(frames) {
  const players = frames[0]?.afterState?.players;
  if (!players) return [];
  return Object.keys(players).sort();
}

export function seriesBounds(series) {
  let min = Infinity;
  let max = -Infinity;
  for (const playerId in series) {
    for (const value of series[playerId]) {
      if (value < min) min = value;
      if (value > max) max = value;
    }
  }
  if (!Number.isFinite(min)) min = 0;
  if (!Number.isFinite(max)) max = 0;
  if (min === max) max = min + 1;
  return { min, max };
}
