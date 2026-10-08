import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import QueueLane from './QueueLane.jsx';

describe('QueueLane', () => {
  it('renders occupied and empty queue slots', () => {
    render(
      <QueueLane
        playerId="player_0"
        queue={[
          { index: 0, label: 'nw_base_1', cardId: 'nw_base_1', empty: false, changed: true },
          { index: 1, label: 'slot 2', cardId: null, empty: true, changed: false },
        ]}
        selectedContext={{ kind: 'queue', playerId: 'player_0', index: 0 }}
      />,
    );

    expect(screen.getByText('nw_base_1')).toBeInTheDocument();
    expect(screen.getByText('slot 2')).toBeInTheDocument();
    expect(screen.getByTestId('queue-slot-player_0-0')).toHaveAttribute('data-changed', 'true');
    expect(screen.getByTestId('queue-slot-player_0-1')).toHaveAttribute('data-changed', 'false');
    expect(screen.getByTestId('queue-slot-player_0-0')).toHaveAttribute('data-selected', 'true');
    expect(screen.getByTestId('queue-slot-player_0-0')).toHaveAccessibleName('nw_base_1, changed, selected');
    expect(screen.getByTestId('queue-slot-player_0-0')).toHaveAttribute('aria-pressed', 'true');
  });

  it('emits selected slot context', () => {
    const onSelect = vi.fn();
    render(<QueueLane onSelect={onSelect} playerId="player_0" queue={[
      { index: 0, label: 'nw_base_1', cardId: 'nw_base_1', empty: false, changed: false },
    ]} />);

    fireEvent.click(screen.getByTestId('queue-slot-player_0-0'));

    expect(onSelect).toHaveBeenCalledWith({ kind: 'queue', playerId: 'player_0', index: 0 });
  });
});
