import { useMemo, useState } from 'react';
import { buildReplayTableViewModel } from '../replay/tableViewModel.js';
import GameTable from './GameTable.jsx';
import PopulationChart from './PopulationChart.jsx';
import Timeline from './Timeline.jsx';
import styles from './ReplayView.module.css';

function ReplayView({
  frames,
  frame,
  safeIndex,
  inspectorMode,
  gameTab,
  conversationArtifacts,
  failureSnapshot,
  filterId,
  query,
  searchIndices,
  isPlaying,
  selectedTurn,
  searchBoxRef,
  onInspectorModeChange,
  onGameTabChange,
  onFilterChange,
  onSelectIndex,
  onQueryChange,
  onSearchStep,
  onTogglePlay,
}) {
  const [selectedContext, setSelectedContext] = useState(null);
  const table = useMemo(
    () => buildReplayTableViewModel({ conversationArtifacts, failureSnapshot, frame }),
    [conversationArtifacts, failureSnapshot, frame],
  );

  function handleSelectContext(nextSelectedContext) {
    setSelectedContext(nextSelectedContext);
  }

  return (
    <>
      <div className={styles.workspace}>
        <GameTable
          gameTab={gameTab}
          inspectorMode={inspectorMode}
          onGameTabChange={onGameTabChange}
          onInspectorModeChange={onInspectorModeChange}
          onSelectContext={handleSelectContext}
          selectedContext={selectedContext}
          table={table}
        />
      </div>
      <div className={styles.chartRow}>
        <PopulationChart frames={frames} selectedTurn={selectedTurn} />
      </div>
      <Timeline
        filterId={filterId}
        frames={frames}
        isPlaying={isPlaying}
        onFilterChange={onFilterChange}
        onQueryChange={onQueryChange}
        onSearchStep={onSearchStep}
        onSelectIndex={onSelectIndex}
        onTogglePlay={onTogglePlay}
        conversationArtifacts={conversationArtifacts}
        failureSnapshot={failureSnapshot}
        query={query}
        ref={searchBoxRef}
        searchIndices={searchIndices}
        selectedIndex={safeIndex}
      />
    </>
  );
}

export default ReplayView;
