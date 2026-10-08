import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { buildReplayTableViewModel } from '../replay/tableViewModel.js';
import GameTable from './GameTable.jsx';

function table() {
  return buildReplayTableViewModel({
    frame: {
      eventIndex: 4,
      event: { event_type: 'cards_enqueued', player_id: 'player_1', payload: { cards: ['nw_base_1'] }, turn: 2 },
      relatedAction: { action_id: 'player_1:place', action_type: 'place', player_id: 'player_1', turn: 2 },
      decisionTrace: null,
      warnings: [],
      deltas: [
        {
          playerId: 'player_1',
          field: 'queue',
          before: [null, null],
          after: ['nw_base_1', null],
          reason: 'cards enqueued',
        },
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
    },
    conversationArtifacts: { messages: [], source: 'none' },
    failureSnapshot: null,
  });
}

describe('GameTable', () => {
  it('renders the table label, event strip metadata, and player tableaus', () => {
    render(<GameTable table={table()} />);

    expect(screen.getByRole('region', { name: 'Nuclear War table' })).toBeInTheDocument();
    const eventStrip = screen.getByRole('group', { name: 'Current event' });
    expect(within(eventStrip).getByRole('heading', { name: 'Cards enqueued' })).toBeInTheDocument();
    expect(within(eventStrip).getByText('Current event')).toBeInTheDocument();
    expect(within(eventStrip).getByText('Event 4')).toBeInTheDocument();
    expect(within(eventStrip).getByText('Turn 2')).toBeInTheDocument();
    expect(within(eventStrip).getByText('Active player 1')).toBeInTheDocument();
    expect(within(eventStrip).getByText('Reconstructed from replay events')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'player 0' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'player 1' })).toBeInTheDocument();
  });

  it('emits selected context from a player control', () => {
    const onSelectContext = vi.fn();
    render(<GameTable onSelectContext={onSelectContext} table={table()} />);

    fireEvent.click(screen.getByRole('button', { name: 'Select player 1' }));

    expect(onSelectContext).toHaveBeenCalledWith({ kind: 'player', playerId: 'player_1' });
  });

  it('passes selected player context to the table and drawer', () => {
    render(<GameTable selectedContext={{ kind: 'player', playerId: 'player_1' }} table={table()} />);

    const playerTableau = screen.getByTestId('player-tableau-player_1');
    expect(playerTableau).toHaveAttribute('data-selected', 'true');
    expect(within(playerTableau).getByRole('button', { name: 'Select player 1' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );

    const summary = screen.getByRole('region', { name: 'Selected table object' });
    expect(within(summary).getByRole('heading', { name: 'player 1' })).toBeInTheDocument();
    expect(within(summary).getByText('12M')).toBeInTheDocument();
    expect(within(summary).getByText('nw_base_1, Slot 2 empty')).toBeInTheDocument();
  });

  it('passes selected queue context to the queue slot and drawer', () => {
    render(<GameTable selectedContext={{ kind: 'queue', playerId: 'player_1', index: 0 }} table={table()} />);

    expect(screen.getByTestId('queue-slot-player_1-0')).toHaveAttribute('data-selected', 'true');
    expect(screen.getByTestId('queue-slot-player_1-0')).toHaveAttribute('aria-pressed', 'true');

    const summary = screen.getByRole('region', { name: 'Selected table object' });
    expect(within(summary).getByRole('heading', { name: 'player 1 queue slot 1' })).toBeInTheDocument();
    expect(within(summary).getByText('nw_base_1')).toBeInTheDocument();
  });
});
