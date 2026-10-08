import { render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { traceArtifactPayload, traceReplayPayload } from '../test/replayFixtures.js';
import ContextDrawer from './ContextDrawer.jsx';

function context(overrides = {}) {
  const replay = traceReplayPayload();
  const trace = traceArtifactPayload();
  const frame = {
    eventIndex: 1,
    event: replay.events[0],
    relatedAction: replay.actions[0],
    decisionTrace: trace.traces[0],
    deltas: [{ playerId: 'player_0', field: 'handCount', before: 9, after: 10 }],
    warnings: [],
  };
  return {
    frame,
    relatedAction: frame.relatedAction,
    decisionTrace: frame.decisionTrace,
    pressMessages: [],
    failureSnapshot: null,
    warnings: [],
    ...overrides,
  };
}

describe('ContextDrawer', () => {
  it('renders the default readable event story without raw event JSON', () => {
    render(<ContextDrawer context={context()} />);
    expect(screen.getByRole('button', { name: 'Game' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('button', { name: 'Event' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getAllByRole('heading', { name: 'Card drawn' }).length).toBeGreaterThan(0);
    expect(screen.getByText('Player 0 drew a card.')).toBeInTheDocument();
    expect(screen.queryByText(/"event_type"/)).not.toBeInTheDocument();
  });

  it('renders agent panel state from the Agent tab', () => {
    render(<ContextDrawer context={context()} gameTab="Agent" inspectorMode="Game" />);
    expect(screen.getByRole('button', { name: 'Agent' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('heading', { name: 'Agent decision' })).toBeInTheDocument();
    expect(screen.getByText('player_0:draw')).toBeInTheDocument();
    expect(screen.getByText('Recovered after 1 retry')).toBeInTheDocument();
  });

  it('renders a compact selected player summary above the active panel', () => {
    render(
      <ContextDrawer
        context={context()}
        selectedContext={{
          kind: 'player',
          playerId: 'player_1',
          player: {
            playerId: 'player_1',
            label: 'player 1',
            populationLabel: '12M',
            aliveLabel: 'Alive',
            warLabel: 'At war',
            queue: [
              { index: 0, cardId: 'nw_base_1' },
              { index: 1, cardId: null },
            ],
          },
        }}
      />,
    );
    const summary = screen.getByRole('region', { name: 'Selected table object' });
    expect(within(summary).getByRole('heading', { name: 'player 1' })).toBeInTheDocument();
    expect(within(summary).getByText('12M')).toBeInTheDocument();
    expect(within(summary).getByText('Alive')).toBeInTheDocument();
    expect(within(summary).getByText('At war')).toBeInTheDocument();
    expect(within(summary).getByText('nw_base_1, Slot 2 empty')).toBeInTheDocument();
    expect(screen.queryByText(/"playerId"/)).not.toBeInTheDocument();
  });

  it('renders a compact selected queue summary above the active panel', () => {
    render(
      <ContextDrawer
        context={context()}
        selectedContext={{
          kind: 'queue',
          playerId: 'player_1',
          index: 0,
          player: { playerId: 'player_1', label: 'player 1' },
          slot: { index: 0, label: 'nw_base_1', cardId: 'nw_base_1', empty: false },
        }}
      />,
    );
    const summary = screen.getByRole('region', { name: 'Selected table object' });
    expect(within(summary).getByRole('heading', { name: 'player 1 queue slot 1' })).toBeInTheDocument();
    expect(within(summary).getByText('nw_base_1')).toBeInTheDocument();
    expect(within(summary).getByText('Occupied')).toBeInTheDocument();
  });

  it('emits segmented control changes from button controls', () => {
    const onInspectorModeChange = vi.fn();
    const onGameTabChange = vi.fn();
    render(
      <ContextDrawer
        context={context()}
        onGameTabChange={onGameTabChange}
        onInspectorModeChange={onInspectorModeChange}
      />,
    );
    screen.getByRole('button', { name: 'Forensic' }).click();
    screen.getByRole('button', { name: 'Conversation' }).click();

    expect(onInspectorModeChange).toHaveBeenCalledWith('Forensic');
    expect(onGameTabChange).toHaveBeenCalledWith('Conversation');
  });

  it('renders no-press and press states in the Conversation tab', () => {
    const { rerender } = render(<ContextDrawer context={context()} gameTab="Conversation" inspectorMode="Game" />);
    expect(screen.getByText('No press messages in this replay.')).toBeInTheDocument();

    rerender(
      <ContextDrawer
        context={context({
          pressMessages: [
            {
              id: 'press-0',
              turn: 1,
              speakerLabel: 'Player 0',
              audienceLabel: 'Public',
              visibility: 'public',
              recipientLabel: 'Unknown',
              commitment: null,
              text: 'Hold fire.',
            },
          ],
        })}
        gameTab="Conversation"
        inspectorMode="Game"
      />,
    );

    expect(screen.getByText('Hold fire.')).toBeInTheDocument();
    expect(screen.getByText('Player 0 to Public')).toBeInTheDocument();
  });

  it('renders forensic event JSON only in Forensic mode', () => {
    render(<ContextDrawer context={context()} inspectorMode="Forensic" />);

    expect(screen.getByRole('button', { name: 'Forensic' })).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByText('Event JSON')).toBeInTheDocument();
    expect(screen.getByText(/"event_type": "card_drawn"/)).toBeInTheDocument();
  });
});
