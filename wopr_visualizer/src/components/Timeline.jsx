import { ChevronLeft, ChevronRight, Pause, Play } from 'lucide-react';
import { forwardRef } from 'react';
import { frameMatchesFilter, REPLAY_FILTERS } from '../replay/replayFilters.js';
import { formatSentenceLabel } from '../replay/replayFormatters.js';
import { timelineMarkerKinds } from '../replay/timelineMarkers.js';
import SearchBox from './SearchBox.jsx';
import styles from './Timeline.module.css';

function Timeline(
  {
    frames,
    selectedIndex,
    filterId,
    isPlaying,
    onFilterChange,
    onSelectIndex,
    onTogglePlay,
    query,
    onQueryChange,
    searchIndices,
    onSearchStep,
    conversationArtifacts,
    failureSnapshot,
  },
  searchBoxRef,
) {
  const selectedFrame = frames[selectedIndex];
  const filteredCount = frames.filter((frame) => frameMatchesFilter(frame, filterId)).length;
  const searchSet = new Set(searchIndices);
  const searchPosition = searchSet.size === 0 ? 0 : [...searchSet].findIndex((i) => i >= selectedIndex) + 1 || searchSet.size;

  function handleRangeChange(event) {
    onSelectIndex(Number(event.target.value));
  }

  function handlePrevious() {
    onSelectIndex(Math.max(0, selectedIndex - 1));
  }

  function handleNext() {
    onSelectIndex(Math.min(frames.length - 1, selectedIndex + 1));
  }

  return (
    <footer className={styles.timeline} aria-label="Event timeline">
      <div className={styles.filters}>
        {REPLAY_FILTERS.map((filter) => (
          <TimelineFilterButton
            active={filter.id === filterId}
            filter={filter}
            key={filter.id}
            onFilterChange={onFilterChange}
          />
        ))}
        <span className={styles.tag}>{filteredCount} matching frames</span>
        <div className={styles.searchSlot}>
          <SearchBox
            onQueryChange={onQueryChange}
            query={query}
            ref={searchBoxRef}
            resultPosition={Math.max(searchPosition, searchSet.size === 0 ? 0 : 1)}
            totalMatches={searchSet.size}
          />
          {query ? (
            <div className={styles.searchNav}>
              <button aria-label="Previous search match" className={styles.iconButton} onClick={() => onSearchStep('prev')} type="button">
                <ChevronLeft size={14} />
              </button>
              <button aria-label="Next search match" className={styles.iconButton} onClick={() => onSearchStep('next')} type="button">
                <ChevronRight size={14} />
              </button>
            </div>
          ) : null}
        </div>
      </div>
      <div className={styles.timelineControls}>
        <div className={styles.toolbar}>
          <button aria-label={isPlaying ? 'Pause' : 'Play'} className={styles.iconButton} onClick={onTogglePlay} type="button">
            {isPlaying ? <Pause size={16} /> : <Play size={16} />}
          </button>
          <button aria-label="Previous event" className={styles.iconButton} onClick={handlePrevious} type="button">
            <ChevronLeft size={16} />
          </button>
          <button aria-label="Next event" className={styles.iconButton} onClick={handleNext} type="button">
            <ChevronRight size={16} />
          </button>
        </div>
        <input
          aria-label="Select event"
          className={styles.range}
          max={frames.length - 1}
          min="0"
          onChange={handleRangeChange}
          type="range"
          value={selectedIndex}
        />
        <span className={styles.tag}>
          {selectedIndex} / {frames.length - 1}: {formatSentenceLabel(selectedFrame.event?.event_type)}
        </span>
      </div>
      <div className={styles.markerRail} aria-hidden="true">
        {frames.map((frame) => (
          <span
            className={markerClass(frame, selectedIndex, searchSet, { ...conversationArtifacts, failureSnapshot })}
            key={frame.eventIndex}
          />
        ))}
      </div>
    </footer>
  );
}

function TimelineFilterButton({ filter, active, onFilterChange }) {
  function handleFilterClick() {
    onFilterChange(filter.id);
  }

  return (
    <button
      className={`${styles.filterButton} ${active ? styles.tabActive : ''}`}
      onClick={handleFilterClick}
      type="button"
    >
      {filter.label}
    </button>
  );
}

function markerClass(frame, selectedIndex, searchSet, markerArtifacts) {
  const classes = [styles.marker];
  if (frame.eventIndex === selectedIndex) classes.push(styles.markerActive);
  if (searchSet.has(frame.eventIndex)) classes.push(styles.markerSearch);
  for (const kind of timelineMarkerKinds(frame, markerArtifacts)) {
    const markerClassName = markerKindClass(kind);
    if (markerClassName) classes.push(markerClassName);
  }
  return classes.join(' ');
}

function markerKindClass(kind) {
  const classNames = {
    decision: styles.markerDecision,
    warning: styles.markerWarning,
    press: styles.markerPress,
    failure: styles.markerFailure,
    launch: styles.markerLaunch,
    detonation: styles.markerDanger,
    elimination: styles.markerDanger,
    stable: styles.markerStable,
  };
  return classNames[kind] ?? null;
}

export default forwardRef(Timeline);
