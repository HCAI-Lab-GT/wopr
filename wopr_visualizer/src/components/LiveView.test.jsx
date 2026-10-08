import { act, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { LiveApiError } from '../live/liveClient.js';
import LiveView from './LiveView.jsx';

function liveSession(overrides = {}) {
  return { session_id: 'seed-42-table', seed: 42, controlled_players: ['player_0'], agent_players: ['player_1'], state_version: 7, status: 'running', ...overrides };
}

function liveState(overrides = {}) {
  const players = [
    livePlayer('player_0', { population: 42, queue: [null, 'nw_base_queue'] }),
    livePlayer('player_1', { population: 18, at_war: true }),
  ];
  return { state_version: 7, turn: 3, source_label: 'live local session', players, recent_events: [], warnings: [], ...overrides };
}

function livePlayer(playerId, overrides = {}) {
  return { player_id: playerId, population: 30, alive: true, at_war: false, hand_count: 6, secret_count: 0, deterrent_count: 0, face_up: null, queue: [null, null], ...overrides };
}

function liveDecision(overrides = {}) {
  return {
    pending: true,
    state_version: 7,
    agent_id: 'player_0',
    decision_type: 'place',
    legal_actions: [{ action_id: 'player_0:place', action_type: 'enqueue', label: 'Place card' }],
    ...overrides,
  };
}

function fakeClient(overrides = {}) {
  const client = { getSession: vi.fn().mockResolvedValue(liveSession()), getState: vi.fn().mockResolvedValue(liveState()) };
  return { ...client, getDecision: vi.fn().mockResolvedValue(liveDecision()), submitDecision: vi.fn().mockResolvedValue({ ok: true, state_version: 8 }), stepAgent: vi.fn().mockResolvedValue({ ok: true, state_version: 8 }), ...overrides };
}

function deferred() {
  let resolve;
  const promise = new Promise((done) => { resolve = done; });
  return { promise, resolve };
}

describe('LiveView', () => {
  it('fetches session, state, decision, and renders the live table', async () => {
    const client = fakeClient();
    render(<LiveView client={client} />);

    const table = await screen.findByRole('region', { name: 'Nuclear War table' });

    expect(client.getSession).toHaveBeenCalledTimes(1);
    expect(client.getState).toHaveBeenCalledTimes(1);
    expect(client.getDecision).toHaveBeenCalledTimes(1);
    expect(screen.getByText('Seed 42')).toBeInTheDocument();
    expect(within(table).getByRole('heading', { name: 'Live decision' })).toBeInTheDocument();
    expect(within(table).getByRole('heading', { name: 'player 0' })).toBeInTheDocument();
    expect(within(table).getByText('42M')).toBeInTheDocument();
  });

  it('submits a legal action and refreshes state and decision', async () => {
    const client = fakeClient({
      getState: vi.fn().mockResolvedValueOnce(liveState()).mockResolvedValueOnce(liveState({ state_version: 8 })),
      getDecision: vi.fn().mockResolvedValueOnce(liveDecision()).mockResolvedValueOnce(liveDecision({ state_version: 8 })),
    });
    render(<LiveView client={client} />);

    fireEvent.click(await screen.findByRole('button', { name: 'Place card' }));

    await waitFor(() => expect(client.submitDecision).toHaveBeenCalledWith('player_0:place', 7));
    await waitFor(() => expect(client.getState).toHaveBeenCalledTimes(2));
    expect(client.getDecision).toHaveBeenCalledTimes(2);
  });

  it('keeps stale-state errors visible', async () => {
    const error = new LiveApiError('stale_state', 'State version changed.', 409);
    render(<LiveView client={fakeClient({ submitDecision: vi.fn().mockRejectedValue(error) })} />);

    fireEvent.click(await screen.findByRole('button', { name: 'Place card' }));

    const alert = await screen.findByRole('alert');
    expect(within(alert).getByText('stale_state')).toBeInTheDocument();
  });

  it('shows Step agent only for agent-player decisions', async () => {
    const client = fakeClient();
    const { rerender } = render(<LiveView client={client} />);

    await screen.findByRole('button', { name: 'Place card' });
    expect(screen.queryByRole('button', { name: 'Step agent' })).not.toBeInTheDocument();

    const agentClient = fakeClient({ getDecision: vi.fn().mockResolvedValue(liveDecision({ agent_id: 'player_1' })) });
    rerender(<LiveView client={agentClient} />);
    expect(await screen.findByRole('button', { name: 'Step agent' })).toBeEnabled();
  });

  it('steps an agent and refreshes state and decision', async () => {
    const client = fakeClient({
      getState: vi.fn().mockResolvedValueOnce(liveState()).mockResolvedValueOnce(liveState({ state_version: 8 })),
      getDecision: vi.fn()
        .mockResolvedValueOnce(liveDecision({ agent_id: 'player_1' }))
        .mockResolvedValueOnce(liveDecision({ agent_id: 'player_1', state_version: 8 })),
    });
    render(<LiveView client={client} />);

    fireEvent.click(await screen.findByRole('button', { name: 'Step agent' }));

    await waitFor(() => expect(client.stepAgent).toHaveBeenCalledWith(7));
    await waitFor(() => expect(client.getState).toHaveBeenCalledTimes(2));
  });

  it('shows an initial refresh error and recovers through manual refresh', async () => {
    const error = new LiveApiError('network_error', 'Network failed.', 0);
    const client = fakeClient({ getSession: vi.fn().mockRejectedValueOnce(error).mockResolvedValue(liveSession()) });
    render(<LiveView client={client} />);

    expect(within(await screen.findByRole('alert')).getByText('network_error')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Refresh' }));

    expect(await screen.findByRole('region', { name: 'Nuclear War table' })).toBeInTheDocument();
    expect(client.getSession).toHaveBeenCalledTimes(2);
  });

  it('does not warn when unmounted during a manual refresh', async () => {
    const sessionRefresh = deferred();
    const stateRefresh = deferred();
    const decisionRefresh = deferred();
    const client = fakeClient({
      getSession: vi.fn().mockResolvedValueOnce(liveSession()).mockReturnValueOnce(sessionRefresh.promise),
      getState: vi.fn().mockResolvedValueOnce(liveState()).mockReturnValueOnce(stateRefresh.promise),
      getDecision: vi.fn().mockResolvedValueOnce(liveDecision()).mockReturnValueOnce(decisionRefresh.promise),
    });
    const { unmount } = render(<LiveView client={client} />);
    await screen.findByRole('button', { name: 'Refresh' });
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    fireEvent.click(screen.getByRole('button', { name: 'Refresh' }));
    unmount();
    await act(async () => {
      sessionRefresh.resolve(liveSession());
      stateRefresh.resolve(liveState({ state_version: 8 }));
      decisionRefresh.resolve(liveDecision({ state_version: 8 }));
      await Promise.all([sessionRefresh.promise, stateRefresh.promise, decisionRefresh.promise]);
    });

    expect(consoleError).not.toHaveBeenCalled();
    consoleError.mockRestore();
  });
});
