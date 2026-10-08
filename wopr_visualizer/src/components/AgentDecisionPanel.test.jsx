import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { traceArtifactPayload, traceReplayPayload } from '../test/replayFixtures.js';
import AgentDecisionPanel from './AgentDecisionPanel.jsx';

describe('AgentDecisionPanel', () => {
  it('renders a readable linked decision trace summary', () => {
    render(
      <AgentDecisionPanel
        frame={{
          relatedAction: traceReplayPayload().actions[0],
          decisionTrace: traceArtifactPayload().traces[0],
        }}
      />,
    );

    expect(screen.getByRole('heading', { name: 'Agent decision' })).toBeInTheDocument();
    expect(screen.getByText('player_0:draw')).toBeInTheDocument();
    expect(screen.getByText('Recovered after 1 retry')).toBeInTheDocument();
    expect(screen.getByText('No legal action_id parsed')).toBeInTheDocument();
    expect(screen.getByText('hosted')).toBeInTheDocument();
    expect(screen.getByText('demo-model')).toBeInTheDocument();
    expect(screen.getByText('choose one action')).toBeInTheDocument();
    expect(screen.getByText('not-json')).toBeInTheDocument();
    expect(screen.queryByText(/"legal_options"/)).not.toBeInTheDocument();
  });

  it('renders an empty state when no trace is linked', () => {
    render(<AgentDecisionPanel frame={{ relatedAction: null, decisionTrace: null }} />);

    expect(screen.getByText('No related decision trace for this event.')).toBeInTheDocument();
  });
});
