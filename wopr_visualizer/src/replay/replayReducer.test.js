import { describe, expect, it } from 'vitest';
import sampleReplay from '../data/sim.json';
import { findRelatedAction } from './actionLinking.js';
import { buildReplayFrames, warningCount } from './replayReducer.js';
import { parseReplayJson } from './replayValidation.js';

const BASE_ACTION = {
  action_id: 'player_0:advance',
  action_type: 'advance',
  payload: {},
  player_id: 'player_0',
  turn: 1,
};

function replayWith(events, actions = [BASE_ACTION]) {
  return {
    mode: 'table',
    seed: 1,
    agent: 'test',
    players: 2,
    turns: 1,
    winner: null,
    termination_reason: 'test',
    final_populations: { player_0: 25, player_1: 25 },
    actions,
    events,
  };
}

describe('replay reducer', () => {
  it('parses JSON and builds one frame per replay event', () => {
    const parsed = parseReplayJson(JSON.stringify(sampleReplay));
    const frames = buildReplayFrames(parsed);

    expect(frames).toHaveLength(sampleReplay.events.length + 1);
    expect(frames[0].event).toBeNull();
    expect(frames[0].afterState.source).toBe('reconstructed from replay events');
    expect(warningCount(frames)).toBeGreaterThan(0);
  });

  it('links reducer frames to nearest turn and actor actions', () => {
    const event = sampleReplay.events.find((item) => item.event_type === 'cards_enqueued');
    const action = findRelatedAction(sampleReplay.actions, event);

    expect(action.action_type).toBe('enqueue');
    expect(action.player_id).toBe(event.player_id);
    expect(action.turn).toBe(event.turn);
  });

  it('tracks queue and face-up state for ready card events', () => {
    const payload = replayWith(
      [
        {
          card_id: null,
          event_type: 'cards_enqueued',
          payload: { cards: ['delivery_card'] },
          player_id: 'player_0',
          turn: 1,
        },
        {
          card_id: 'delivery_card',
          event_type: 'delivery_ready',
          payload: { capacity: 1 },
          player_id: 'player_0',
          turn: 1,
        },
      ],
      [{ ...BASE_ACTION, action_type: 'enqueue' }],
    );

    const readyFrame = buildReplayFrames(payload).at(-1);

    expect(readyFrame.afterState.players.player_0.faceUp).toBe('delivery_card');
    expect(readyFrame.afterState.players.player_0.queue).toEqual([null, null]);
    expect(readyFrame.deltas.some((delta) => delta.field === 'faceUp')).toBe(true);
  });

  it('continues after unsupported events and records a warning', () => {
    const payload = replayWith([
      {
        card_id: null,
        event_type: 'frontend_unknown_event',
        payload: { observed: true },
        player_id: 'player_0',
        turn: 1,
      },
    ]);

    const frame = buildReplayFrames(payload)[1];

    expect(frame.afterState.players.player_0.population).toBe(25);
    expect(frame.warnings).toEqual([
      {
        eventIndex: 1,
        eventType: 'frontend_unknown_event',
        message: 'No reducer handler for this event.',
      },
    ]);
  });

  it('rejects invalid JSON and missing replay fields', () => {
    expect(() => parseReplayJson('{')).toThrow(/not valid JSON/);
    expect(() => parseReplayJson(JSON.stringify({ mode: 'table' }))).toThrow(/missing required field/);
  });
});
