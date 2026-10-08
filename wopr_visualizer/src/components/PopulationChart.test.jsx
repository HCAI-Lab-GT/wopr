import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import PopulationChart from './PopulationChart.jsx';

function frame(eventIndex, turn, populations) {
  const players = Object.fromEntries(
    Object.entries(populations).map(([id, population]) => [id, { playerId: id, population }]),
  );
  return { eventIndex, afterState: { turn, players } };
}

const frames = [
  frame(0, 0, { player_0: 25, player_1: 25 }),
  frame(1, 1, { player_0: 25, player_1: 25 }),
  frame(2, 1, { player_0: 20, player_1: 25 }),
  frame(3, 2, { player_0: 20, player_1: 18 }),
];

describe('PopulationChart', () => {
  it('renders the chart with a legend entry per player', () => {
    render(<PopulationChart frames={frames} />);
    expect(screen.getByText('player 0')).toBeInTheDocument();
    expect(screen.getByText('player 1')).toBeInTheDocument();
    expect(screen.getByRole('img', { name: 'Population chart' })).toBeInTheDocument();
  });

  it('renders one polyline per player', () => {
    const { container } = render(<PopulationChart frames={frames} />);
    const lines = container.querySelectorAll('polyline');
    expect(lines).toHaveLength(2);
  });

  it('invokes onSelectTurn when a point is clicked', () => {
    const onSelectTurn = vi.fn();
    const { container } = render(<PopulationChart frames={frames} onSelectTurn={onSelectTurn} />);
    const points = container.querySelectorAll('circle');
    fireEvent.click(points[points.length - 1]);
    expect(onSelectTurn).toHaveBeenCalled();
  });

  it('renders nothing problematic when frames have a single player', () => {
    const single = [frame(0, 0, { player_0: 10 }), frame(1, 1, { player_0: 8 })];
    const { container } = render(<PopulationChart frames={single} />);
    expect(container.querySelectorAll('polyline')).toHaveLength(1);
  });
});
