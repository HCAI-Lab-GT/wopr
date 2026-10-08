import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import LiveView from './LiveView.jsx';

function clientFor(agentId) {
  return {
    getSession: vi.fn().mockResolvedValue({
      session_id: 'seed-42-table',
      seed: 42,
      status: 'running',
      controlled_players: ['player_0'],
      agent_players: ['player_1'],
    }),
    getState: vi.fn().mockResolvedValue({
      state_version: 7,
      turn: 3,
      source_label: 'live local session',
      players: [
        player('player_0'),
        player('player_1'),
      ],
      recent_events: [],
      warnings: [],
    }),
    getDecision: vi.fn().mockResolvedValue({
      pending: true,
      state_version: 7,
      agent_id: agentId,
      decision_type: 'place',
      legal_actions: [{ action_id: `${agentId}:place`, action_type: 'enqueue', label: 'Place card' }],
    }),
    submitDecision: vi.fn(),
    stepAgent: vi.fn(),
  };
}

function player(playerId) {
  return {
    player_id: playerId,
    population: 30,
    alive: true,
    at_war: false,
    hand_count: 6,
    secret_count: 0,
    deterrent_count: 0,
    face_up: null,
    queue: [null, null],
  };
}

describe('LiveView seat gating', () => {
  it('shows legal actions only for controlled-player decisions', async () => {
    render(<LiveView client={clientFor('player_0')} />);

    expect(await screen.findByRole('button', { name: 'Place card' })).toBeEnabled();
    expect(screen.queryByRole('button', { name: 'Step agent' })).not.toBeInTheDocument();
  });

  it('shows Step agent only for agent-player decisions', async () => {
    render(<LiveView client={clientFor('player_1')} />);

    expect(await screen.findByRole('button', { name: 'Step agent' })).toBeEnabled();
    expect(screen.queryByRole('button', { name: 'Place card' })).not.toBeInTheDocument();
  });
});
