const EVENT_ACTION_HINTS = {
  card_drawn: ['draw'],
  cards_enqueued: ['enqueue'],
  target_declared: ['target'],
  launch_declared: ['resolve', 'target'],
  spinner_result: ['resolve'],
  warhead_detonated: ['resolve'],
  intercept_success: ['resolve'],
};

export function findRelatedAction(actions, event) {
  const sameTurn = actions.filter((action) => action.turn === event.turn);
  const sameActor = sameTurn.filter((action) => action.player_id === event.player_id);
  const candidates = sameActor.length > 0 ? sameActor : sameTurn;
  const hints = EVENT_ACTION_HINTS[event.event_type] || [];
  const hinted = [...candidates].reverse().find((action) => {
    return hints.includes(action.action_type);
  });
  if (hinted) {
    return hinted;
  }
  return candidates.at(-1) || null;
}
