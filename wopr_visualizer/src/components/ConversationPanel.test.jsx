import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import ConversationPanel from './ConversationPanel.jsx';

describe('ConversationPanel', () => {
  it('renders no-press empty state', () => {
    render(<ConversationPanel conversationArtifacts={{ messages: [], source: 'none' }} frame={{ event: null }} />);

    expect(screen.getByText('No press messages in this replay.')).toBeInTheDocument();
  });

  it('renders public and private press messages from artifacts', () => {
    render(
      <ConversationPanel
        conversationArtifacts={{
          source: 'press',
          messages: [
            {
              id: 'press-0',
              turn: 2,
              speakerLabel: 'Player 0',
              audienceLabel: 'Public',
              visibility: 'public',
              recipientLabel: 'Unknown',
              commitment: null,
              text: 'Hold fire.',
            },
            {
              id: 'press-1',
              turn: 3,
              speakerLabel: 'Player 1',
              audienceLabel: 'Player 0',
              recipientLabel: 'Player 0',
              visibility: 'private',
              commitment: null,
              text: 'I will intercept.',
            },
          ],
        }}
        frame={{ event: { turn: 2 } }}
      />,
    );

    expect(screen.getByText('Hold fire.')).toBeInTheDocument();
    expect(screen.getByText('I will intercept.')).toBeInTheDocument();
    expect(screen.getByText('Player 0 to Public')).toBeInTheDocument();
    expect(screen.getByText('Player 1 whispered to Player 0')).toBeInTheDocument();
  });

  it('renders a commitment badge when a message carries a commitment', () => {
    render(
      <ConversationPanel
        conversationArtifacts={{
          source: 'press',
          messages: [
            {
              id: 'press-0',
              turn: 2,
              speakerLabel: 'Player 0',
              audienceLabel: 'Public',
              visibility: 'public',
              recipientLabel: 'Unknown',
              commitment: { kind: 'stand_down', target_round: 3 },
              text: 'Hold fire.',
            },
          ],
        }}
        frame={{ event: { turn: 2 } }}
      />,
    );

    expect(screen.getByTestId('commitment-badge')).toHaveTextContent(
      'Commitment: stand_down · round 3',
    );
  });
});
