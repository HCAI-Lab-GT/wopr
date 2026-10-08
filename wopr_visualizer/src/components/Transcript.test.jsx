import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import Transcript from './Transcript.jsx';

const events = [
  { event_type: 'launch_declared', player_id: 'player_0', payload: { target: 'player_1' } },
  { event_type: 'warhead_detonated', player_id: 'player_1', payload: { warhead: 'nw_base_abc', extra: 1, more: 2 } },
  { event_type: 'peace_restored' },
];

describe('Transcript', () => {
  it('renders a row per event with formatted type and actor', () => {
    render(<Transcript events={events} selectedIndex={1} onSelectIndex={() => {}} />);

    expect(screen.getByText('Launch declared')).toBeInTheDocument();
    expect(screen.getByText('player 0')).toBeInTheDocument();
    expect(screen.getByText('Warhead detonated')).toBeInTheDocument();
    expect(screen.getByText('Peace restored')).toBeInTheDocument();
  });

  it('marks the selected row as current and jumps on click', () => {
    const onSelectIndex = vi.fn();
    render(<Transcript events={events} selectedIndex={2} onSelectIndex={onSelectIndex} />);

    const detonatedRow = screen.getByText('Warhead detonated').closest('button');
    expect(detonatedRow).toHaveAttribute('aria-current', 'true');

    fireEvent.click(screen.getByText('Peace restored'));
    expect(onSelectIndex).toHaveBeenLastCalledWith(3);
  });

  it('summarizes payload keys, collapsing beyond two', () => {
    render(<Transcript events={events} selectedIndex={1} onSelectIndex={() => {}} />);

    expect(screen.getByText(/target: player_1/)).toBeInTheDocument();
    expect(screen.getByText(/\+1/)).toBeInTheDocument();
  });

  it('renders the empty state when no events', () => {
    render(<Transcript events={[]} selectedIndex={0} onSelectIndex={() => {}} />);

    expect(screen.getByText('No transcript data in this replay.')).toBeInTheDocument();
  });
});
