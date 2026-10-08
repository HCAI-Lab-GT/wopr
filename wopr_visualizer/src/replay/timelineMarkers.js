export function timelineMarkerKinds(frame, artifacts = {}) {
  const kinds = ['event'];
  const eventType = frame.event?.event_type ?? '';
  if (frame.decisionTrace) kinds.push('decision');
  if ((frame.warnings ?? []).length > 0) kinds.push('warning');
  if (hasPressMessage(frame, artifacts)) kinds.push('press');
  if (hasFailure(frame, artifacts)) kinds.push('failure');
  if (isLaunch(eventType)) kinds.push('launch');
  if (eventType === 'warhead_detonated') kinds.push('detonation');
  if (eventType === 'eliminated') kinds.push('elimination');
  if (eventType === 'intercept_success' || eventType === 'peace_restored') kinds.push('stable');
  return kinds;
}

function hasPressMessage(frame, artifacts) {
  const turn = frame.event?.turn ?? frame.afterState?.turn;
  return (artifacts.messages ?? []).some((message) => message.turn === turn);
}

function hasFailure(frame, artifacts) {
  const failure = artifacts.failureSnapshot?.decision_failure;
  if (!failure) return false;
  const turn = frame.event?.turn ?? frame.afterState?.turn;
  return failure.turn === turn;
}

function isLaunch(eventType) {
  return eventType === 'launch_declared' || eventType === 'target_declared' || eventType === 'cards_enqueued';
}
