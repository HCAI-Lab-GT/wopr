import { useMemo, useState } from 'react';
import {
  nextSearchIndex,
  previousSearchIndex,
  searchResultIndices,
} from '../replay/searchMatches.js';

const DEFAULT_INSPECTOR_MODE = 'Game';
const DEFAULT_GAME_TAB = 'Event';
const DEFAULT_FILTER = 'all';
const DEFAULT_QUERY = '';

export function useWorkbenchNavigation(frames) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [inspectorMode, setInspectorMode] = useState(DEFAULT_INSPECTOR_MODE);
  const [gameTab, setGameTab] = useState(DEFAULT_GAME_TAB);
  const [filterId, setFilterId] = useState(DEFAULT_FILTER);
  const [query, setQuery] = useState(DEFAULT_QUERY);
  const [error, setError] = useState('');
  const maxIndex = Math.max(0, frames.length - 1);
  const safeIndex = Math.min(Math.max(0, selectedIndex), maxIndex);
  const searchIndices = useMemo(() => searchResultIndices(frames, query), [frames, query]);

  function resetNavigation() {
    setSelectedIndex(0);
    setInspectorMode(DEFAULT_INSPECTOR_MODE);
    setGameTab(DEFAULT_GAME_TAB);
    setFilterId(DEFAULT_FILTER);
    setQuery(DEFAULT_QUERY);
    setError('');
  }

  function handleSearchStep(direction) {
    if (searchIndices.length === 0) return;
    const nextIndex = direction === 'next'
      ? nextSearchIndex(searchIndices, safeIndex)
      : previousSearchIndex(searchIndices, safeIndex);
    setSelectedIndex(nextIndex);
  }

  return {
    error,
    filterId,
    gameTab,
    handleSearchStep,
    inspectorMode,
    query,
    resetNavigation,
    safeIndex,
    searchIndices,
    selectedIndex,
    setError,
    setFilterId,
    setGameTab,
    setInspectorMode,
    setQuery,
    setSelectedIndex,
  };
}
