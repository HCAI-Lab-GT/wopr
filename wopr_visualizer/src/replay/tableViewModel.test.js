import { describe, expect, it } from 'vitest';
import { buildReplayTableViewModel } from './tableViewModel.js';

function frame() {
  return {
    eventIndex: 4,
    event: { event_type: 'cards_enqueued', player_id: 'player_1', payload: { cards: ['nw_base_1'] }, turn: 2 },
    relatedAction: { action_id: 'player_1:place', action_type: 'place', player_id: 'player_1', turn: 2 },
    decisionTrace: { trace_id: 'player_1:2:1', selected_action_id: 'player_1:place' },
    warnings: [{ message: 'No reducer handler for this event.' }],
    deltas: [
      { playerId: 'player_1', field: 'queue', before: [null, null], after: ['nw_base_1', null], reason: 'cards enqueued' },
      { playerId: 'player_1', field: 'handCount', before: 8, after: 7, reason: 'cards enqueued' },
    ],
    afterState: {
      source: 'reconstructed from replay events',
      turn: 2,
      phase: 'replay',
      players: {
        player_0: {
          playerId: 'player_0',
          population: 40,
          handCount: 7,
          secretCount: 1,
          deterrentCount: 0,
          faceUp: null,
          queue: [null, null],
          alive: true,
          atWar: false,
        },
        player_1: {
          playerId: 'player_1',
          population: 12,
          handCount: 7,
          secretCount: 0,
          deterrentCount: 2,
          faceUp: 'nw_base_face',
          queue: ['nw_base_1', null],
          alive: true,
          atWar: true,
        },
      },
    },
  };
}

describe('buildReplayTableViewModel', () => {
  it('maps replay frame state into table players and zones', () => {
    const model = buildReplayTableViewModel({
      frame: frame(),
      conversationArtifacts: { messages: [], source: 'none' },
      failureSnapshot: null,
    });

    expect(model.source).toBe('replay');
    expect(model.eventTitle).toBe('Cards enqueued');
    expect(model.activePlayerId).toBe('player_1');
    expect(model.players).toHaveLength(2);
    expect(model.players[1]).toMatchObject({
      playerId: 'player_1',
      label: 'player 1',
      population: 12,
      aliveLabel: 'Alive',
      warLabel: 'At war',
      changed: true,
    });
    expect(model.players[1].zones.hand.value).toBe('7');
    expect(model.players[1].zones.secrets.value).toBe('0');
    expect(model.players[1].zones.deterrents.value).toBe('2');
    expect(model.players[1].zones.faceUp.value).toBe('nw_base_face');
    expect(model.players[1].queue[0]).toMatchObject({ index: 0, label: 'nw_base_1', empty: false, changed: true });
    expect(model.players[1].queue[1]).toMatchObject({ index: 1, label: 'Slot 2', empty: true, changed: false });
  });

  it('marks population and status fields when their deltas changed', () => {
    const statusFrame = frame();
    statusFrame.deltas = [
      ...statusFrame.deltas,
      { playerId: 'player_1', field: 'population', before: 12, after: 10, reason: 'population loss' },
      { playerId: 'player_1', field: 'alive', before: true, after: false, reason: 'eliminated' },
      { playerId: 'player_1', field: 'atWar', before: false, after: true, reason: 'war declared' },
    ];
    statusFrame.afterState.players.player_1.population = 10;
    statusFrame.afterState.players.player_1.alive = false;
    statusFrame.afterState.players.player_1.atWar = true;

    const model = buildReplayTableViewModel({
      frame: statusFrame,
      conversationArtifacts: { messages: [], source: 'none' },
      failureSnapshot: null,
    });

    expect([model.players[0].populationChanged, model.players[0].aliveChanged, model.players[0].warChanged]).toEqual([
      false,
      false,
      false,
    ]);
    expect([model.players[1].populationChanged, model.players[1].aliveChanged, model.players[1].warChanged]).toEqual([
      true,
      true,
      true,
    ]);
  });

  it('normalizes initial frames and filters unrelated evidence turns', () => {
    const initialFrame = frame();
    initialFrame.eventIndex = 0;
    initialFrame.event = null;
    initialFrame.relatedAction = null;
    initialFrame.decisionTrace = null;
    initialFrame.deltas = [];
    initialFrame.afterState.turn = 1;

    const model = buildReplayTableViewModel({
      frame: initialFrame,
      conversationArtifacts: {
        source: 'press',
        messages: [{ id: 'm1', turn: 2, speaker: 'player_0', text: 'Hold fire.' }],
      },
      failureSnapshot: { decision_failure: { turn: 2, player_id: 'player_1' } },
    });

    expect(model).toMatchObject({ eventTitle: 'Initial state', activePlayerId: null });
    expect(model.context.pressMessages).toEqual([]);
    expect(model.context.failureSnapshot).toBeNull();
  });

  it('links selected context to evidence records', () => {
    const model = buildReplayTableViewModel({
      frame: frame(),
      conversationArtifacts: {
        source: 'press',
        messages: [{ id: 'm1', turn: 2, speaker: 'player_0', text: 'Hold fire.' }],
      },
      failureSnapshot: { decision_failure: { turn: 2, player_id: 'player_1' } },
    });

    expect(model.context.relatedAction.action_id).toBe('player_1:place');
    expect(model.context.decisionTrace.trace_id).toBe('player_1:2:1');
    expect(model.context.pressMessages).toHaveLength(1);
    expect(model.context.failureSnapshot.decision_failure.player_id).toBe('player_1');
    expect(model.context.warnings).toEqual(['No reducer handler for this event.']);
  });
});
