import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import EventStoryPanel from './EventStoryPanel.jsx';

describe('EventStoryPanel', () => {
  it('renders readable event story, deltas, and warnings without raw JSON', () => {
    render(
      <EventStoryPanel
        frame={{
          event: { event_type: 'card_drawn', payload: {}, player_id: 'player_0', turn: 1 },
          deltas: [{ playerId: 'player_0', field: 'handCount', before: 9, after: 10 }],
          warnings: [{ message: 'Frontend reconstruction warning.' }],
        }}
      />,
    );

    expect(screen.getByRole('heading', { name: 'Card drawn' })).toBeInTheDocument();
    expect(screen.getByText('Player 0 drew a card.')).toBeInTheDocument();
    expect(screen.getByText('Player 0 hand count: 9 to 10.')).toBeInTheDocument();
    expect(screen.getByText('Frontend reconstruction warning.')).toBeInTheDocument();
    expect(screen.queryByText(/"event_type"/)).not.toBeInTheDocument();
  });
});
