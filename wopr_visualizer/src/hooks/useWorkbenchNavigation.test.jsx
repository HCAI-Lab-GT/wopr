import { renderHook, act } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { useWorkbenchNavigation } from './useWorkbenchNavigation.js';

const frames = [
  { eventIndex: 0, event: null },
  { eventIndex: 1, event: { event_type: 'card_drawn', player_id: 'player_0', payload: {} } },
  { eventIndex: 2, event: { event_type: 'warhead_detonated', player_id: 'player_1', payload: {} } },
];

describe('useWorkbenchNavigation', () => {
  it('starts in the readable replay view state', () => {
    const { result } = renderHook(() => useWorkbenchNavigation(frames));

    expect(result.current.safeIndex).toBe(0);
    expect(result.current.inspectorMode).toBe('Game');
    expect(result.current.gameTab).toBe('Event');
    expect(result.current.filterId).toBe('all');
    expect(result.current.query).toBe('');
    expect(result.current.error).toBe('');
  });

  it('resets navigation and import error state', () => {
    const { result } = renderHook(() => useWorkbenchNavigation(frames));

    act(() => {
      result.current.setSelectedIndex(2);
      result.current.setInspectorMode('Forensic');
      result.current.setGameTab('Conversation');
      result.current.setFilterId('combat');
      result.current.setQuery('detonated');
      result.current.setError('bad file');
    });
    act(() => result.current.resetNavigation());

    expect(result.current.safeIndex).toBe(0);
    expect(result.current.inspectorMode).toBe('Game');
    expect(result.current.gameTab).toBe('Event');
    expect(result.current.filterId).toBe('all');
    expect(result.current.query).toBe('');
    expect(result.current.error).toBe('');
  });

  it('clamps negative selected indices to the first frame', () => {
    const { result } = renderHook(() => useWorkbenchNavigation(frames));

    act(() => result.current.setSelectedIndex(-1));

    expect(result.current.safeIndex).toBe(0);
  });

  it('steps through search matches without changing frame data', () => {
    const { result } = renderHook(() => useWorkbenchNavigation(frames));

    act(() => result.current.setQuery('warhead'));
    act(() => result.current.handleSearchStep('next'));

    expect(result.current.safeIndex).toBe(2);
    expect(result.current.searchIndices).toEqual([2]);
  });

  it('steps backward through previous search matches', () => {
    const { result } = renderHook(() => useWorkbenchNavigation(frames));

    act(() => {
      result.current.setQuery('player_');
      result.current.setSelectedIndex(2);
    });
    act(() => result.current.handleSearchStep('prev'));

    expect(result.current.safeIndex).toBe(1);
    expect(result.current.searchIndices).toEqual([1, 2]);
  });
});
