import { FolderOpen, FileJson, Upload, RotateCcw, Layers, Palette } from 'lucide-react';
import styles from './ImportBar.module.css';

const THEME_SCREEN = 'screen';
const THEME_PAPER = 'paper';

function ImportBar({
  payload,
  selectedIndex,
  totalEvents,
  traceTotal,
  pressTotal,
  warningTotal,
  error,
  summary,
  view,
  liveApiUrl,
  theme = THEME_SCREEN,
  failureSnapshotLoaded,
  onFileChange,
  onTraceFileChange,
  onPressFileChange,
  onFailureSnapshotChange,
  onBatchDirChange,
  onLiveApiUrlChange,
  onLoadSample,
  onLoadSampleBatch,
  onThemeChange,
  onViewChange,
}) {
  const isLiveView = view === 'live';

  function handleLiveApiUrlInputChange(event) {
    onLiveApiUrlChange(event.target.value);
  }

  return (
    <header className={styles.topBar}>
      <div className={styles.brandBlock}>
        <p className={styles.eyebrow}>Nuclear War replay debugger</p>
        <h1 className={styles.title}>Replay workbench</h1>
        <div className={styles.statusLine}>
          <span>Mode {payload.mode}</span>
          <span>Agent {payload.agent}</span>
          <span>Seed {payload.seed}</span>
          <span>Event {selectedIndex} / {totalEvents}</span>
          <span>Reducer warnings {warningTotal}</span>
          <span>Decision traces {traceTotal}</span>
          <span>Press messages {pressTotal}</span>
          {failureSnapshotLoaded ? <span>Failure snapshot loaded</span> : null}
        </div>
        {error ? <p className={styles.warningPill}>{error}</p> : null}
      </div>
      <div className={styles.toolbar}>
        <ViewToggle hasBatchSummary={Boolean(summary)} view={view} onViewChange={onViewChange} />
        <ThemeToggle theme={theme} onThemeChange={onThemeChange} />
        {isLiveView ? (
          <label className={styles.apiUrlField}>
            <span className={styles.apiUrlLabel}>API URL</span>
            <input
              aria-label="Live API URL"
              className={styles.apiUrlInput}
              onChange={handleLiveApiUrlInputChange}
              type="url"
              value={liveApiUrl}
            />
          </label>
        ) : null}
        <label className={styles.button}>
          <FolderOpen size={16} aria-hidden="true" />
          Load batch directory
          <input
            // directory selection via webkitdirectory; plain file input fallback used by Playwright
            {...directoryProps()}
            className={styles.fileInput}
            type="file"
            accept=".json,application/json"
            multiple
            onChange={onBatchDirChange}
          />
        </label>
        <button className={styles.button} type="button" onClick={onLoadSampleBatch}>
          <Layers size={16} aria-hidden="true" />
          Sample batch
        </button>
        <label className={styles.button}>
          <Upload size={16} aria-hidden="true" />
          Load replay
          <input className={styles.fileInput} type="file" accept=".json,application/json" onChange={onFileChange} />
        </label>
        <label className={styles.button}>
          <FileJson size={16} aria-hidden="true" />
          Load traces
          <input className={styles.fileInput} type="file" accept=".json,application/json" onChange={onTraceFileChange} />
        </label>
        <label className={styles.button}>
          <FileJson size={16} aria-hidden="true" />
          Load press
          <input className={styles.fileInput} type="file" accept=".json,application/json" onChange={onPressFileChange} />
        </label>
        <label className={styles.button}>
          <FileJson size={16} aria-hidden="true" />
          Load failure
          <input className={styles.fileInput} type="file" accept=".json,application/json" onChange={onFailureSnapshotChange} />
        </label>
        <button className={styles.button} type="button" onClick={onLoadSample}>
          <RotateCcw size={16} aria-hidden="true" />
          Sample replay
        </button>
      </div>
    </header>
  );
}

function ThemeToggle({ theme, onThemeChange }) {
  function handleScreenClick() {
    onThemeChange?.(THEME_SCREEN);
  }

  function handlePaperClick() {
    onThemeChange?.(THEME_PAPER);
  }

  return (
    <div className={styles.themeToggle} role="group" aria-label="Visual theme">
      <span className={styles.themeIcon}>
        <Palette size={14} aria-hidden="true" />
      </span>
      <button
        aria-pressed={theme === THEME_SCREEN}
        className={`${styles.toggleButton} ${theme === THEME_SCREEN ? styles.toggleActive : ''}`}
        onClick={handleScreenClick}
        type="button"
      >
        Screen
      </button>
      <button
        aria-pressed={theme === THEME_PAPER}
        className={`${styles.toggleButton} ${theme === THEME_PAPER ? styles.toggleActive : ''}`}
        onClick={handlePaperClick}
        type="button"
      >
        Paper
      </button>
    </div>
  );
}

function ViewToggle({ hasBatchSummary, view, onViewChange }) {
  function handleReplayClick() {
    onViewChange('replay');
  }

  function handleBatchClick() {
    onViewChange('batch');
  }

  function handleLiveClick() {
    onViewChange('live');
  }

  return (
    <div className={styles.viewToggle} role="tablist" aria-label="Active view">
      <button
        aria-selected={view === 'replay'}
        className={`${styles.toggleButton} ${view === 'replay' ? styles.toggleActive : ''}`}
        onClick={handleReplayClick}
        role="tab"
        type="button"
      >
        Replay
      </button>
      <button
        aria-selected={view === 'batch'}
        className={`${styles.toggleButton} ${view === 'batch' ? styles.toggleActive : ''}`}
        disabled={!hasBatchSummary}
        onClick={handleBatchClick}
        role="tab"
        type="button"
      >
        Batch
      </button>
      <button
        aria-selected={view === 'live'}
        className={`${styles.toggleButton} ${view === 'live' ? styles.toggleActive : ''}`}
        onClick={handleLiveClick}
        role="tab"
        type="button"
      >
        Live
      </button>
    </div>
  );
}

function directoryProps() {
  return { webkitdirectory: '', directory: '' };
}

export default ImportBar;
