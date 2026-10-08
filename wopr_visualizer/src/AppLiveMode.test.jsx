import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import App from './App.jsx';

describe('Replay workbench live mode', () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it('shows live controls and keeps the default local API URL editable', async () => {
    const fetchStub = vi.fn(() => Promise.reject(new Error('offline')));
    vi.stubGlobal('fetch', fetchStub);

    render(<App />);

    const liveButton = screen.getByRole('tab', { name: 'Live' });
    expect(liveButton).toBeInTheDocument();

    fireEvent.click(liveButton);

    const apiUrlInput = screen.getByLabelText('Live API URL');
    expect(apiUrlInput).toHaveValue('http://127.0.0.1:8765');
    expect(screen.getByRole('region', { name: 'Live workbench' })).toBeInTheDocument();
    expect(screen.getByText('No live table state loaded.')).toBeInTheDocument();

    await waitFor(() => expect(fetchStub).toHaveBeenCalledWith('http://127.0.0.1:8765/session', { method: 'GET' }));
    fetchStub.mockClear();

    fireEvent.change(apiUrlInput, { target: { value: 'http://localhost:9000' } });
    expect(apiUrlInput).toHaveValue('http://localhost:9000');
    await waitFor(() => expect(fetchStub).toHaveBeenCalledWith('http://localhost:9000/session', { method: 'GET' }));
  });

  it('stops replay playback when switching to live mode', async () => {
    vi.useFakeTimers();
    vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('offline'))));

    render(<App />);

    expect(screen.getByText('Event 0 / 174')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'Play' }));
    fireEvent.click(screen.getByRole('tab', { name: 'Live' }));

    await act(async () => {
      vi.advanceTimersByTime(2100);
    });

    expect(screen.getByText('Event 0 / 174')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('tab', { name: 'Replay' }));
    expect(screen.getByRole('button', { name: 'Play' })).toBeInTheDocument();
  });

  it('does not restart replay playback from Space while live mode is active', async () => {
    vi.useFakeTimers();
    vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('offline'))));

    render(<App />);

    fireEvent.click(screen.getByRole('tab', { name: 'Live' }));
    fireEvent.keyDown(window, { key: ' ' });

    await act(async () => {
      vi.advanceTimersByTime(2100);
    });

    expect(screen.getByText('Event 0 / 174')).toBeInTheDocument();
  });
});
