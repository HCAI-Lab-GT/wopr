import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import PlayerTableau from './PlayerTableau.jsx';

const player = {
  playerId: 'player_1',
  label: 'player 1',
  population: 12,
  populationLabel: '12M',
  populationChanged: true,
  aliveLabel: 'Alive',
  aliveChanged: false,
  warLabel: 'At war',
  warChanged: true,
  active: true,
  changed: true,
  zones: {
    hand: { label: 'Hand', value: '7', changed: true },
    secrets: { label: 'Secrets', value: '0', changed: false },
    deterrents: { label: 'Deterrents', value: '2', changed: false },
    faceUp: { label: 'Face up', value: 'nw_base_face', changed: false },
  },
  queue: [
    { index: 0, label: 'nw_base_1', cardId: 'nw_base_1', empty: false, changed: true },
    { index: 1, label: 'Slot 2', cardId: null, empty: true, changed: false },
  ],
  deltas: [{ field: 'handCount', before: 8, after: 7, reason: 'cards enqueued' }],
};

describe('PlayerTableau', () => {
  it('renders player table state', () => {
    render(<PlayerTableau player={player} />);

    expect(screen.getByRole('heading', { name: 'player 1' })).toBeInTheDocument();
    expect(screen.getByText('12M')).toBeInTheDocument();
    expect(screen.getByText('Alive')).toBeInTheDocument();
    expect(screen.getByText('At war')).toBeInTheDocument();
    expect(screen.getByText('nw_base_face')).toBeInTheDocument();
    expect(screen.getByText('Hand count: 8 to 7')).toBeInTheDocument();
    expect(screen.getByTestId('player-population-player_1')).toHaveAttribute('data-changed', 'true');
    expect(screen.getByTestId('player-alive-player_1')).toHaveAttribute('data-changed', 'false');
    expect(screen.getByTestId('player-war-player_1')).toHaveAttribute('data-changed', 'true');
  });

  it('emits player selection', () => {
    const onSelect = vi.fn();
    render(
      <PlayerTableau
        onSelect={onSelect}
        player={player}
        selectedContext={{ kind: 'player', playerId: 'player_1' }}
      />,
    );

    const selectButton = screen.getByRole('button', { name: 'Select player 1' });
    expect(selectButton).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByTestId('player-tableau-player_1')).toHaveAttribute('data-selected', 'true');

    fireEvent.click(selectButton);

    expect(onSelect).toHaveBeenCalledWith({ kind: 'player', playerId: 'player_1' });
  });

  it('does not select the player from the non-interactive tableau body', () => {
    const onSelect = vi.fn();
    render(<PlayerTableau onSelect={onSelect} player={player} />);

    fireEvent.click(screen.getByTestId('player-tableau-player_1'));

    expect(onSelect).not.toHaveBeenCalled();
  });

  it('emits queue selection without player selection', () => {
    const onSelect = vi.fn();
    render(<PlayerTableau onSelect={onSelect} player={player} />);

    fireEvent.click(screen.getByTestId('queue-slot-player_1-0'));

    expect(onSelect).toHaveBeenCalledTimes(1);
    expect(onSelect).toHaveBeenCalledWith({ kind: 'queue', playerId: 'player_1', index: 0 });
  });
});
