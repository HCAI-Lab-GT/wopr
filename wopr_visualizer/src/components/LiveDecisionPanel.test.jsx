import { fireEvent, render, screen, within } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import { LiveApiError } from '../live/liveClient.js';
import LiveDecisionPanel from './LiveDecisionPanel.jsx';

function pendingDecision(overrides = {}) {
  return {
    pending: true,
    state_version: 12,
    agent_id: 'player_1',
    decision_type: 'launch_target',
    legal_actions: [
      {
        action_id: 'player_1:target:player_0',
        action_type: 'launch_target',
        label: 'Target player 0',
      },
      {
        action_id: 'player_1:target:player_2',
        action_type: 'launch_target',
        label: 'Target player 2',
      },
    ],
    ...overrides,
  };
}

describe('LiveDecisionPanel', () => {
  it('renders pending owner, decision type, and legal action buttons', () => {
    render(<LiveDecisionPanel decision={pendingDecision()} />);

    expect(screen.getByRole('heading', { name: 'Pending decision' })).toBeInTheDocument();
    expect(screen.getByText('player 1')).toBeInTheDocument();
    expect(screen.getByText('Launch target')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Target player 0' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Target player 2' })).toBeInTheDocument();
  });

  it('calls onSubmitAction with the action id and state version', () => {
    const onSubmitAction = vi.fn();
    render(<LiveDecisionPanel canSubmitAction decision={pendingDecision()} onSubmitAction={onSubmitAction} />);

    fireEvent.click(screen.getByRole('button', { name: 'Target player 0' }));

    expect(onSubmitAction).toHaveBeenCalledWith('player_1:target:player_0', 12);
  });

  it('does not expose legal action buttons when action submission is unavailable', () => {
    const onSubmitAction = vi.fn();
    render(<LiveDecisionPanel canSubmitAction={false} decision={pendingDecision()} onSubmitAction={onSubmitAction} />);

    expect(screen.queryByRole('button', { name: 'Target player 0' })).not.toBeInTheDocument();
    expect(screen.getByText('Manual action selection is unavailable for this seat.')).toBeInTheDocument();
    expect(onSubmitAction).not.toHaveBeenCalled();
  });

  it('calls onStepAgent with the current state version', () => {
    const onStepAgent = vi.fn();
    render(<LiveDecisionPanel canStepAgent decision={pendingDecision()} onStepAgent={onStepAgent} />);

    fireEvent.click(screen.getByRole('button', { name: 'Step agent' }));

    expect(onStepAgent).toHaveBeenCalledWith(12);
  });

  it('gates agent-step controls by seat ownership', () => {
    const onStepAgent = vi.fn();
    const { rerender } = render(
      <LiveDecisionPanel canStepAgent={false} decision={pendingDecision()} onStepAgent={onStepAgent} />,
    );

    expect(screen.queryByRole('button', { name: 'Step agent' })).not.toBeInTheDocument();

    rerender(<LiveDecisionPanel canStepAgent decision={pendingDecision()} onStepAgent={onStepAgent} />);
    fireEvent.click(screen.getByRole('button', { name: 'Step agent' }));

    expect(onStepAgent).toHaveBeenCalledWith(12);
  });

  it('disables legal action buttons while submitting', () => {
    render(<LiveDecisionPanel decision={pendingDecision()} submitting />);

    expect(screen.getByRole('button', { name: 'Target player 0' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Target player 2' })).toBeDisabled();
  });

  it('does not submit mutations without a numeric state version', () => {
    const onStepAgent = vi.fn();
    const onSubmitAction = vi.fn();
    render(
      <LiveDecisionPanel
        canStepAgent
        decision={pendingDecision({ state_version: undefined })}
        onStepAgent={onStepAgent}
        onSubmitAction={onSubmitAction}
      />,
    );

    expect(screen.getByRole('button', { name: 'Target player 0' })).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Step agent' })).toBeDisabled();
    fireEvent.click(screen.getByRole('button', { name: 'Target player 0' }));
    fireEvent.click(screen.getByRole('button', { name: 'Step agent' }));
    expect(onSubmitAction).not.toHaveBeenCalled();
    expect(onStepAgent).not.toHaveBeenCalled();
  });

  it('disables refresh while submitting', () => {
    render(<LiveDecisionPanel decision={pendingDecision()} onRefresh={vi.fn()} submitting />);

    expect(screen.getByRole('button', { name: 'Refresh' })).toBeDisabled();
  });

  it('shows structured API errors', () => {
    const error = new LiveApiError('stale_state', 'State version changed.', 409);
    render(<LiveDecisionPanel decision={pendingDecision()} error={error} />);

    const alert = screen.getByRole('alert');
    expect(within(alert).getByText('stale_state')).toBeInTheDocument();
    expect(within(alert).getByText('State version changed.')).toBeInTheDocument();
    expect(within(alert).getByText('HTTP 409')).toBeInTheDocument();
  });
});
