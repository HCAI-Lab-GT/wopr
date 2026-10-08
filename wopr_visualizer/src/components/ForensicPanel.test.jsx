import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { traceArtifactPayload, traceReplayPayload } from '../test/replayFixtures.js';
import ForensicPanel from './ForensicPanel.jsx';

function failureSnapshot() {
  return {
    decision_failure: {
      player_id: 'player_0',
      turn: 1,
      decision_type: 'draw',
      agent_identity: { name: 'Analyst Zero' },
      legal_options: [{ action_id: 'player_0:draw', label: 'Draw' }],
      validation_errors: ['No action_id parsed'],
      raw_visible_responses: ['bad'],
    },
  };
}

describe('ForensicPanel', () => {
  it('renders raw replay, trace, prompt, response, parse, and failure data', () => {
    render(
      <ForensicPanel
        failureSnapshot={failureSnapshot()}
        frame={{
          event: traceReplayPayload().events[0],
          relatedAction: traceReplayPayload().actions[0],
          decisionTrace: traceArtifactPayload().traces[0],
        }}
      />,
    );

    expect(screen.getByText('Event JSON')).toBeInTheDocument();
    expect(screen.getByText(/"event_type": "card_drawn"/)).toBeInTheDocument();
    expect(screen.getByText('Related action JSON')).toBeInTheDocument();
    expect(screen.getByText('Decision trace JSON')).toBeInTheDocument();
    expect(screen.getByText('Prompt history')).toBeInTheDocument();
    expect(screen.getByText('Raw response history')).toBeInTheDocument();
    expect(screen.getByText('Parse result')).toBeInTheDocument();
    expect(screen.getByText('Failure snapshot')).toBeInTheDocument();
    expect(screen.getAllByText(/"validation_errors"/).length).toBeGreaterThan(0);
  });
});
