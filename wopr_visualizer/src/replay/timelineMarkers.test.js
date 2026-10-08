import { describe, expect, it } from 'vitest';
import { timelineMarkerKinds } from './timelineMarkers.js';

function frame(eventType, extras = {}) {
  return {
    eventIndex: 2,
    event: { event_type: eventType, turn: 2, payload: {}, player_id: 'player_0' },
    warnings: [],
    ...extras,
  };
}

describe('timelineMarkerKinds', () => {
  it('returns additive event, decision, warning, and press markers', () => {
    const markers = timelineMarkerKinds(
      frame('launch_declared', {
        decisionTrace: { selected_action_id: 'player_0:launch' },
        warnings: [{ message: 'warning' }],
      }),
      { messages: [{ turn: 2, text: 'Hold fire.' }] },
    );

    expect(markers).toEqual(['event', 'decision', 'warning', 'press', 'launch']);
  });

  it.each([
    ['warhead_detonated', 'detonation'],
    ['eliminated', 'elimination'],
  ])('marks %s as %s', (eventType, marker) => {
    expect(timelineMarkerKinds(frame(eventType), { messages: [] })).toContain(marker);
  });

  it('marks failed diagnostic frames when a failure snapshot is present', () => {
    const markers = timelineMarkerKinds(frame('card_drawn'), {
      messages: [],
      failureSnapshot: { decision_failure: { turn: 2 } },
    });

    expect(markers).toContain('failure');
  });
});
