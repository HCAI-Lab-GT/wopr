import { act, fireEvent, renderHook } from '@testing-library/react';
import { useState } from 'react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useReplayPlayback } from './useReplayPlayback.js';

function renderPlayback({ frameCount = 5, startIndex = 0, rateMs = 50 } = {}) {
  const setFrameIndex = vi.fn();
  const onSearchFocus = vi.fn();
  const result = renderHook(
    ({ frameIndex }) =>
      useReplayPlayback({ frameIndex, frameCount, setFrameIndex, onSearchFocus, rateMs }),
    { initialProps: { frameIndex: startIndex } },
  );
  return { result, setFrameIndex, onSearchFocus };
}

function pressKey(key, opts = {}) {
  fireEvent.keyDown(window, { key, ...opts });
}

describe('useReplayPlayback keyboard scrubbing', () => {
  it('ArrowRight advances and ArrowLeft retreats, clamped at bounds', () => {
    const { setFrameIndex } = renderPlayback({ frameCount: 5, startIndex: 2 });

    pressKey('ArrowRight');
    expect(setFrameIndex).toHaveBeenLastCalledWith(3);

    pressKey('ArrowLeft');
    expect(setFrameIndex).toHaveBeenLastCalledWith(1);
  });

  it('ArrowLeft does not undershoot 0', () => {
    const { setFrameIndex } = renderPlayback({ frameCount: 5, startIndex: 0 });

    pressKey('ArrowLeft');
    expect(setFrameIndex).toHaveBeenLastCalledWith(0);
  });

  it('Home jumps to first and End to last', () => {
    const { setFrameIndex } = renderPlayback({ frameCount: 6, startIndex: 3 });

    pressKey('Home');
    expect(setFrameIndex).toHaveBeenLastCalledWith(0);

    pressKey('End');
    expect(setFrameIndex).toHaveBeenLastCalledWith(5);
  });

  it('ignores keys while typing in an input', () => {
    const { setFrameIndex } = renderPlayback({ startIndex: 2 });
    const input = document.createElement('input');
    document.body.appendChild(input);
    input.focus();

    fireEvent.keyDown(input, { key: 'ArrowRight' });
    expect(setFrameIndex).not.toHaveBeenCalled();
    document.body.removeChild(input);
  });

  it('ignores keys with modifier held', () => {
    const { setFrameIndex } = renderPlayback({ startIndex: 2 });

    pressKey('ArrowRight', { ctrlKey: true });
    expect(setFrameIndex).not.toHaveBeenCalled();
  });

  it('"/" focuses search', () => {
    const { onSearchFocus } = renderPlayback({ startIndex: 1 });

    pressKey('/');
    expect(onSearchFocus).toHaveBeenCalledTimes(1);
  });
});

describe('useReplayPlayback auto-advance', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('Space toggles play and the interval steps forward then stops at the end', () => {
    let latest = 0;
    const setFrameIndex = vi.fn((updater) => {
      latest = typeof updater === 'function' ? updater(latest) : updater;
    });
    const { result } = renderHook(() =>
      useReplayPlayback({ frameIndex: latest, frameCount: 2, setFrameIndex, rateMs: 50 }),
    );

    expect(result.current.isPlaying).toBe(false);
    act(() => result.current.togglePlay());
    expect(result.current.isPlaying).toBe(true);

    act(() => vi.advanceTimersByTime(50));
    expect(latest).toBe(1);

    act(() => vi.advanceTimersByTime(100));
    expect(latest).toBe(1);
    expect(result.current.isPlaying).toBe(false);
  });

  it('does not start playing when frameCount is 1', () => {
    const setFrameIndex = vi.fn();
    const { result } = renderHook(() =>
      useReplayPlayback({ frameIndex: 0, frameCount: 1, setFrameIndex, rateMs: 50 }),
    );

    act(() => result.current.togglePlay());
    expect(result.current.isPlaying).toBe(false);
  });
});

describe('useReplayPlayback stateful integration', () => {
  beforeEach(() => vi.useFakeTimers());
  afterEach(() => vi.useRealTimers());

  it('steps through frames via real state', () => {
    let stateRef = { current: 0 };
    const { result, rerender } = renderHook(() => {
      const [index, setIndex] = useState(0);
      stateRef.current = index;
      const playback = useReplayPlayback({
        frameIndex: index,
        frameCount: 4,
        setFrameIndex: setIndex,
        rateMs: 50,
      });
      return { index, playback };
    });

    pressKey('ArrowRight');
    rerender();
    expect(result.current.index).toBe(1);

    act(() => result.current.playback.togglePlay());
    act(() => vi.advanceTimersByTime(50));
    rerender();
    expect(result.current.index).toBe(2);

    act(() => vi.advanceTimersByTime(50));
    rerender();
    expect(result.current.index).toBe(3);

    act(() => vi.advanceTimersByTime(50));
    rerender();
    expect(result.current.index).toBe(3);
    expect(result.current.playback.isPlaying).toBe(false);
  });
});
