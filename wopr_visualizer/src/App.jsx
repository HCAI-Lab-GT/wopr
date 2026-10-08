import { useMemo, useRef, useState } from 'react';
import styles from './App.module.css';
import ErrorBoundary from './ErrorBoundary.jsx';
import BatchView from './components/BatchView.jsx';
import ImportBar from './components/ImportBar.jsx';
import LiveView from './components/LiveView.jsx';
import ReplayView from './components/ReplayView.jsx';
import sampleBatchSummary from './data/batch_summary.json';
import * as sampleBatchFiles from './data/sampleBatchFiles.js';
import sampleReplay from './data/sim.json';
import { useWorkbenchNavigation } from './hooks/useWorkbenchNavigation.js';
import { useReplayPlayback } from './hooks/useReplayPlayback.js';
import { buildReplayFrames, warningCount } from './replay/replayReducer.js';
import { parseReplayJson } from './replay/replayValidation.js';
import { parseBatchSummaryJson } from './replay/batchValidation.js';
import { parseFailureSnapshotJson } from './replay/failureSnapshots.js';
import { normalizePressArtifacts, parsePressArtifactJson } from './replay/pressArtifacts.js';
import { parseTraceArtifactJson } from './replay/traceArtifacts.js';

const [VIEW_REPLAY, VIEW_BATCH, VIEW_LIVE] = ['replay', 'batch', 'live'];
const DEFAULT_LIVE_API_URL = 'http://127.0.0.1:8765';

function App() {
  const [payload, setPayload] = useState(sampleReplay);
  const [traceArtifact, setTraceArtifact] = useState(null);
  const [pressArtifact, setPressArtifact] = useState(null);
  const [failureSnapshot, setFailureSnapshot] = useState(null);
  const [summary, setSummary] = useState(null);
  const [dirFiles, setDirFiles] = useState(new Map());
  const [view, setView] = useState(VIEW_REPLAY);
  const [theme, setTheme] = useState('screen');
  const [liveApiUrl, setLiveApiUrl] = useState(DEFAULT_LIVE_API_URL);
  const [selectedSeed, setSelectedSeed] = useState(null);
  const searchBoxRef = useRef(null);

  const frames = useMemo(() => buildReplayFrames(payload, traceArtifact), [payload, traceArtifact]);
  const navigation = useWorkbenchNavigation(frames);
  const frame = frames[navigation.safeIndex];
  const warnings = warningCount(frames);
  const selectedTurn = frame?.afterState?.turn ?? 0;
  const conversationArtifacts = useMemo(() => normalizePressArtifacts(pressArtifact), [pressArtifact]);

  const playback = useReplayPlayback({
    enabled: view === VIEW_REPLAY,
    frameIndex: navigation.safeIndex,
    frameCount: frames.length,
    setFrameIndex: navigation.setSelectedIndex,
    onSearchFocus: () => {
      searchBoxRef.current?.focus();
      searchBoxRef.current?.select();
    },
  });
  const { isPlaying, pause, togglePlay } = playback;

  function resetReplayState() {
    navigation.resetNavigation();
    setFailureSnapshot(null);
  }

  const handleLoadSample = () => {
    setPayload(sampleReplay);
    setTraceArtifact(null);
    setPressArtifact(null);
    resetReplayState();
    setView(VIEW_REPLAY);
  };

  const handleFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const nextPayload = parseReplayJson(await file.text());
      setPayload(nextPayload);
      setTraceArtifact(null);
      setPressArtifact(null);
      resetReplayState();
      setView(VIEW_REPLAY);
    } catch (nextError) {
      navigation.setError(nextError.message);
    } finally {
      event.target.value = '';
    }
  };

  const handleFailureSnapshotChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      setFailureSnapshot(parseFailureSnapshotJson(await file.text()));
      navigation.setError('');
    } catch (nextError) {
      navigation.setError(nextError.message);
    } finally {
      event.target.value = '';
    }
  };

  const handleTraceFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      setTraceArtifact(parseTraceArtifactJson(await file.text(), payload));
      navigation.setError('');
    } catch (nextError) {
      navigation.setError(nextError.message);
    } finally {
      event.target.value = '';
    }
  };

  const handlePressFileChange = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      setPressArtifact(parsePressArtifactJson(await file.text(), payload));
      navigation.setError('');
    } catch (nextError) {
      navigation.setError(nextError.message);
    } finally {
      event.target.value = '';
    }
  };

  const handleBatchDirChange = async (event) => {
    const fileList = event.target.files;
    if (!fileList || fileList.length === 0) return;
    const files = new Map();
    for (const file of fileList) {
      files.set(file.name, file);
    }
    const summaryFile = files.get('summary.json');
    if (!summaryFile) {
      navigation.setError('No summary.json found in selected directory.');
      return;
    }
    try {
      const nextSummary = parseBatchSummaryJson(await summaryFile.text());
      setDirFiles(files);
      setSummary(nextSummary);
      navigation.setError('');
      pause();
      setView(VIEW_BATCH);
    } catch (nextError) {
      navigation.setError(nextError.message);
    } finally {
      event.target.value = '';
    }
  };

  const handleLoadSampleBatch = () => {
    setDirFiles(new Map(sampleBatchFiles.files));
    setSummary(sampleBatchSummary);
    navigation.setError('');
    pause();
    setView(VIEW_BATCH);
    setSelectedSeed(null);
  };

  const handleSelectRun = async (row) => {
    const replayFile = dirFiles.get(row.replayPath);
    if (!replayFile) return;
    try {
      const nextPayload = parseReplayJson(await replayFile.text());
      const traceFile = dirFiles.get(row.tracePath);
      const nextTraceArtifact = traceFile ? parseTraceArtifactJson(await traceFile.text(), nextPayload) : null;
      setPayload(nextPayload);
      setTraceArtifact(nextTraceArtifact);
      resetReplayState();
      setSelectedSeed(row.seed);
      setView(VIEW_REPLAY);
    } catch (nextError) {
      navigation.setError(nextError.message);
    }
  };

  const handleViewChange = (nextView) => { if (nextView !== VIEW_REPLAY) pause(); setView(nextView); };

  return (
    <ErrorBoundary>
      <main className={styles.app} data-theme={theme}>
        <ImportBar
          error={navigation.error}
          failureSnapshotLoaded={Boolean(failureSnapshot)}
          liveApiUrl={liveApiUrl}
          onBatchDirChange={handleBatchDirChange}
          onFailureSnapshotChange={handleFailureSnapshotChange}
          onFileChange={handleFileChange}
          onLiveApiUrlChange={setLiveApiUrl}
          onLoadSample={handleLoadSample}
          onLoadSampleBatch={handleLoadSampleBatch}
          onThemeChange={setTheme}
          onPressFileChange={handlePressFileChange}
          onTraceFileChange={handleTraceFileChange}
          onViewChange={handleViewChange}
          payload={payload}
          pressTotal={pressArtifact?.messages.length ?? 0}
          selectedIndex={navigation.safeIndex}
          summary={summary}
          theme={theme}
          totalEvents={frames.length - 1}
          traceTotal={traceArtifact?.traces.length ?? 0}
          view={view}
          warningTotal={warnings}
        />
        {view === VIEW_LIVE ? (
          <LiveView
            apiUrl={liveApiUrl}
            gameTab={navigation.gameTab}
            inspectorMode={navigation.inspectorMode}
            onGameTabChange={navigation.setGameTab}
            onInspectorModeChange={navigation.setInspectorMode}
          />
        ) : view === VIEW_BATCH && summary ? (
          <BatchView
            dirFiles={dirFiles}
            onSelectRun={handleSelectRun}
            selectedSeed={selectedSeed}
            summary={summary}
          />
        ) : (
          <ReplayView
            conversationArtifacts={conversationArtifacts}
            filterId={navigation.filterId}
            frame={frame}
            frames={frames}
            gameTab={navigation.gameTab}
            failureSnapshot={failureSnapshot}
            inspectorMode={navigation.inspectorMode}
            isPlaying={isPlaying}
            onFilterChange={navigation.setFilterId}
            onGameTabChange={navigation.setGameTab}
            onInspectorModeChange={navigation.setInspectorMode}
            onQueryChange={navigation.setQuery}
            onSearchStep={navigation.handleSearchStep}
            onSelectIndex={navigation.setSelectedIndex}
            onTogglePlay={togglePlay}
            query={navigation.query}
            safeIndex={navigation.safeIndex}
            searchBoxRef={searchBoxRef}
            searchIndices={navigation.searchIndices}
            selectedTurn={selectedTurn}
          />
        )}
      </main>
    </ErrorBoundary>
  );
}

export default App;
