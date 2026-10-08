import BatchSummary from './BatchSummary.jsx';
import RunList from './RunList.jsx';
import styles from './BatchView.module.css';

function BatchView({ summary, dirFiles, onSelectRun, selectedSeed }) {
  return (
    <div className={styles.batchView}>
      <BatchSummary summary={summary} />
      <RunList
        dirFiles={dirFiles}
        onSelectRun={onSelectRun}
        selectedSeed={selectedSeed}
        summary={summary}
      />
    </div>
  );
}

export default BatchView;
