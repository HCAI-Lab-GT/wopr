import { describe, expect, it } from 'vitest';
import { buildEventStory } from './eventStories.js';

function frame(event, extras = {}) {
  return {
    eventIndex: 1,
    event,
    deltas: [],
    warnings: [],
    ...extras,
  };
}

describe('buildEventStory', () => {
  it('summarizes initial state', () => {
    expect(buildEventStory(frame(null))).toMatchObject({
      title: 'Initial state',
      body: 'Replay reconstruction starts from inferred player state.',
    });
  });

  it.each([
    ['card_drawn', {}, 'Player 0 drew a card.'],
    ['cards_enqueued', { cards: ['a', 'b'] }, 'Player 0 added 2 cards to the launch queue.'],
    ['launch_declared', {}, 'Player 0 declared a launch.'],
    ['target_declared', { target: 'player_1' }, 'Player 0 targeted Player 1.'],
    ['warhead_detonated', { target: 'player_1', yield: 10 }, 'Player 0 detonated a warhead against Player 1 for 10 population.'],
    ['intercept_success', {}, 'Player 0 intercepted the attack.'],
    ['eliminated', {}, 'Player 0 was eliminated.'],
    ['peace_restored', {}, 'Peace was restored.'],
  ])('summarizes %s', (eventType, payload, body) => {
    const story = buildEventStory(frame({ event_type: eventType, payload, player_id: 'player_0', turn: 1 }));

    expect(story.body).toBe(body);
    expect(story.title).toMatch(/^[A-Z]/);
  });

  it('includes state deltas and warnings', () => {
    const story = buildEventStory(
      frame(
        { event_type: 'frontend_unknown_event', payload: {}, player_id: 'player_1', turn: 1 },
        {
          deltas: [{ playerId: 'player_1', field: 'population', before: 25, after: 15 }],
          warnings: [{ message: 'No reducer handler for this event.' }],
        },
      ),
    );

    expect(story.title).toBe('Frontend unknown event');
    expect(story.consequences).toContain('Player 1 population: 25 to 15.');
    expect(story.warnings).toEqual(['No reducer handler for this event.']);
  });
});
