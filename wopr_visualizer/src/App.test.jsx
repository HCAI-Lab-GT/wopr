import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import App from './App.jsx';
import { traceArtifact, traceReplay, unsupportedReplay } from './test/replayFixtures.js';

function makeFile(contents, name = 'replay.json') {
  return new File([contents], name, { type: 'application/json' });
}

describe('Replay workbench app', () => {
  it('loads the bundled sample replay into the table and context drawer', () => {
    render(<App />);
    expect(screen.getByText('Replay workbench')).toBeInTheDocument();
    expect(screen.getByRole('region', { name: 'Nuclear War table' })).toBeInTheDocument();
    expect(screen.getByRole('group', { name: 'Current event' })).toBeInTheDocument();
    expect(screen.getByText(/reconstructed from replay events/i)).toBeInTheDocument();
    const contextMode = screen.getByRole('group', { name: 'Context mode' });
    const gameContextTabs = screen.getByRole('group', { name: 'Game context tabs' });
    expect(within(contextMode).getByRole('button', { name: /Game/ })).toHaveAttribute('aria-pressed', 'true');
    expect(within(gameContextTabs).getByRole('button', { name: 'Event' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getAllByRole('heading', { name: 'Initial state' }).length).toBeGreaterThan(0);
    expect(screen.queryByText(/"event_type"/)).not.toBeInTheDocument();
  });

  it('switches between screen and paper visual themes', () => {
    render(<App />);
    const themeControls = screen.getByRole('group', { name: 'Visual theme' });
    const appShell = screen.getByRole('main');

    expect(appShell).toHaveAttribute('data-theme', 'screen');
    fireEvent.click(within(themeControls).getByRole('button', { name: 'Paper' }));
    expect(appShell).toHaveAttribute('data-theme', 'paper');
    fireEvent.click(within(themeControls).getByRole('button', { name: 'Screen' }));
    expect(appShell).toHaveAttribute('data-theme', 'screen');
  });

  it('shows invalid JSON import errors without clearing the sample replay', async () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText(/load replay/i), {
      target: { files: [makeFile('{', 'bad.json')] },
    });
    expect(await screen.findByText(/Replay file is not valid JSON/)).toBeInTheDocument();
    expect(screen.getByText('Replay workbench')).toBeInTheDocument();
  });

  it('scrubs events and switches inspector tabs', () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText('Select event'), { target: { value: '4' } });
    const currentEvent = screen.getByRole('group', { name: 'Current event' });
    expect(within(currentEvent).getByRole('heading', { name: /cards enqueued/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Agent' }));
    expect(screen.getByText('No related decision trace for this event.')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Conversation' }));
    expect(screen.getByText('No press messages in this replay.')).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Forensic' }));
    expect(screen.getByText('Event JSON')).toBeInTheDocument();
    expect(screen.getByText(/"event_type"/)).toBeInTheDocument();
    expect(screen.getByText(/Event 4 \/ 174/)).toBeInTheDocument();
  });

  it('updates the context drawer from visible table select controls', () => {
    render(<App />);
    const playerTableau = screen.getByTestId('player-tableau-player_0');
    fireEvent.click(within(playerTableau).getByRole('button', { name: 'Select player 0' }));

    const playerSummary = screen.getByRole('region', { name: 'Selected table object' });
    expect(within(playerSummary).getByRole('heading', { name: 'player 0' })).toBeInTheDocument();
    expect(within(playerSummary).getByText('Population')).toBeInTheDocument();
    expect(within(playerSummary).getByText('Queue')).toBeInTheDocument();
    expect(within(playerTableau).getByRole('button', { name: 'Select player 0' })).toHaveAttribute(
      'aria-pressed',
      'true',
    );
    fireEvent.click(screen.getByTestId('queue-slot-player_0-0'));

    const queueSummary = screen.getByRole('region', { name: 'Selected table object' });
    expect(within(queueSummary).getByRole('heading', { name: 'player 0 queue slot 1' })).toBeInTheDocument();
    expect(screen.getByTestId('queue-slot-player_0-0')).toHaveAttribute('aria-pressed', 'true');
  });

  it('renders unsupported reducer warnings after importing a replay', async () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText(/load replay/i), {
      target: { files: [makeFile(unsupportedReplay())] },
    });

    await waitFor(() => {
      expect(screen.getByText('0 / 1: Initial state')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByLabelText('Select event'), { target: { value: '1' } });

    expect(screen.getByText('No reducer handler for this event.')).toBeInTheDocument();
    expect(screen.getByText('Reducer warnings 1')).toBeInTheDocument();
  });

  it('imports decision traces and renders them in the Decision tab', async () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText(/load replay/i), {
      target: { files: [makeFile(traceReplay(), 'trace-replay.json')] },
    });
    await screen.findByText('Event 0 / 1');

    fireEvent.change(screen.getByLabelText(/load traces/i), {
      target: { files: [makeFile(traceArtifact(), 'trace-replay.traces.json')] },
    });
    await screen.findByText('Decision traces 1');

    fireEvent.change(screen.getByLabelText('Select event'), { target: { value: '1' } });
    fireEvent.click(screen.getByRole('button', { name: 'Agent' }));

    expect(screen.getByRole('heading', { name: 'Agent decision' })).toBeInTheDocument();
    expect(screen.getByText('player_0:draw')).toBeInTheDocument();
    expect(screen.getByText('Recovered after 1 retry')).toBeInTheDocument();
    expect(screen.getByText('No legal action_id parsed')).toBeInTheDocument();
    expect(screen.getByText('choose one action')).toBeInTheDocument();
    expect(screen.getByText('not-json')).toBeInTheDocument();
    expect(screen.getByText('hosted')).toBeInTheDocument();
    expect(screen.getByText('demo-model')).toBeInTheDocument();
    expect(screen.getByText('12 tokens')).toBeInTheDocument();
  });

  it('imports a failure snapshot and renders it on the matching turn in Forensic mode', async () => {
    render(<App />);
    fireEvent.change(screen.getByLabelText(/load failure/i), {
      target: { files: [makeFile(failureSnapshot(), 'failure_snapshot.json')] },
    });

    await screen.findByText('Failure snapshot loaded');
    fireEvent.click(screen.getByRole('button', { name: 'Forensic' }));
    expect(screen.queryByText('Failure snapshot')).not.toBeInTheDocument();

    fireEvent.change(screen.getByLabelText('Select event'), { target: { value: '1' } });
    const failureSection = screen.getByText('Failure snapshot').closest('section');
    expect(failureSection).not.toBeNull();
    expect(within(failureSection).getByText(/"player_id": "player_0"/)).toBeInTheDocument();
    expect(within(failureSection).getByText(/"decision_type": "draw"/)).toBeInTheDocument();
    expect(within(failureSection).getByText(/"legal_options"/)).toBeInTheDocument();
    expect(within(failureSection).getByText(/"validation_errors"/)).toBeInTheDocument();
  });
});

function failureSnapshot() {
  return JSON.stringify({
    decision_failure: {
      agent_identity: { name: 'Analyst Zero' },
      player_id: 'player_0',
      turn: 1,
      decision_type: 'draw',
      legal_options: [{ action_id: 'player_0:draw', label: 'Draw' }],
      validation_errors: ['No action_id parsed'],
      raw_visible_responses: ['bad'],
    },
  });
}
