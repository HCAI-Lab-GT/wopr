import { describe, expect, it } from 'vitest';
import { buildLiveTableViewModel } from './liveTableViewModel.js';

function liveState(overrides = {}) {
  return {
    state_version: 7,
    turn: 3,
    source_label: 'seed 42 live table',
    players: [
      {
        player_id: 'player_0',
        population: 42,
        alive: true,
        at_war: false,
        hand_count: 6,
        secret_count: 1,
        deterrent_count: 0,
        face_up: null,
        queue: [null, 'nw_base_queue'],
      },
      {
        player_id: 'player_1',
        population: 18,
        alive: true,
        at_war: true,
        hand_count: 4,
        secret_count: 0,
        deterrent_count: 2,
        face_up: 'nw_base_face',
        queue: ['nw_base_launch', null],
      },
    ],
    recent_events: [{ event_type: 'card_drawn', player_id: 'player_0', turn: 3, payload: {} }],
    warnings: ['Live warning'],
    ...overrides,
  };
}

describe('buildLiveTableViewModel', () => {
  it('maps source labels and live decision metadata', () => {
    const model = buildLiveTableViewModel({
      state: liveState(),
      decision: { pending: true, state_version: 7, agent_id: 'player_1', legal_actions: [] },
    });

    expect(model).toMatchObject({
      source: 'live',
      sourceLabel: 'Seed 42 live table',
      eventIndex: 7,
      eventTitle: 'Live decision',
      turn: 3,
      activePlayerId: 'player_1',
    });
    expect(model.players[1]).toMatchObject({
      playerId: 'player_1',
      label: 'player 1',
      population: 18,
      populationLabel: '18M',
      aliveLabel: 'Alive',
      warLabel: 'At war',
      active: true,
      changed: false,
    });
  });

  it('maps player zones and queue slots for GameTable', () => {
    const model = buildLiveTableViewModel({
      state: liveState(),
      decision: { pending: true, state_version: 7, agent_id: 'player_0', legal_actions: [] },
    });

    const player = model.players[0];
    expect(player.zones.hand).toEqual({ label: 'Hand', value: '6', empty: false, changed: false });
    expect(player.zones.secrets).toEqual({ label: 'Secrets', value: '1', empty: false, changed: false });
    expect(player.zones.deterrents).toEqual({ label: 'Deterrents', value: '0', empty: true, changed: false });
    expect(player.zones.faceUp).toEqual({ label: 'Face up', value: 'unknown', empty: true, changed: false });
    expect(player.queue).toEqual([
      { index: 0, label: 'Slot 1', cardId: null, empty: true, changed: false },
      { index: 1, label: 'nw_base_queue', cardId: 'nw_base_queue', empty: false, changed: false },
    ]);
  });

  it('keeps pending decision and frame context available', () => {
    const decision = {
      pending: true,
      state_version: 7,
      agent_id: 'player_1',
      decision_type: 'place',
      legal_actions: [{ action_id: 'player_1:place', label: 'Place card' }],
    };
    const model = buildLiveTableViewModel({ state: liveState(), decision });

    expect(model.context.pendingDecision).toBe(decision);
    expect(model.context.recentEvents).toHaveLength(1);
    expect(model.context.warnings).toEqual(['Live warning']);
    expect(model.context.frame).toMatchObject({
      event: null,
      eventIndex: 7,
      deltas: [],
      relatedAction: null,
      warnings: [{ message: 'Live warning' }],
    });
    expect(model.context.frame.afterState.players.player_0.playerId).toBe('player_0');
  });

  it('preserves raw live player counts in frame state', () => {
    const state = liveState({
      players: [
        {
          player_id: 'player_0',
          population: 42,
          alive: true,
          at_war: false,
          hand_count: undefined,
          secret_count: 1,
          deterrent_count: 0,
          face_up: null,
          queue: [],
        },
      ],
    });

    const model = buildLiveTableViewModel({ state, decision: { pending: false, state_version: 7 } });
    const framePlayer = model.context.frame.afterState.players.player_0;

    expect(framePlayer).toMatchObject({
      handCount: undefined,
      secretCount: 1,
      deterrentCount: 0,
    });
    expect(Number.isNaN(framePlayer.handCount)).toBe(false);
  });

  it('returns a valid table without a pending decision', () => {
    const model = buildLiveTableViewModel({
      state: liveState({ source_label: undefined, warnings: undefined }),
      decision: { pending: false, state_version: 7 },
    });

    expect(model.sourceLabel).toBe('Live local session');
    expect(model.activePlayerId).toBeNull();
    expect(model.players).toHaveLength(2);
    expect(model.context.pendingDecision).toEqual({ pending: false, state_version: 7 });
    expect(model.context.warnings).toEqual([]);
    expect(model.context.frame.afterState.turn).toBe(3);
  });
});
