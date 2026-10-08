import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import CardZone from './CardZone.jsx';

describe('CardZone', () => {
  it('renders a labeled table zone', () => {
    render(<CardZone zoneId="face-up" zone={{ label: 'face up', value: 'nw_base_1', changed: false }} />);

    expect(screen.getByText('face up')).toBeInTheDocument();
    expect(screen.getByText('nw_base_1')).toBeInTheDocument();
  });

  it('marks changed and selected zones by stable id', () => {
    render(<CardZone selected zoneId="cards-in-hand" zone={{ label: 'hand', value: '7', changed: true }} />);

    expect(screen.getByTestId('card-zone-cards-in-hand')).toHaveAttribute('data-changed', 'true');
    expect(screen.getByTestId('card-zone-cards-in-hand')).toHaveAttribute('data-selected', 'true');
    expect(screen.getByTestId('card-zone-cards-in-hand')).toHaveAccessibleName('hand, changed, selected');
  });
});
