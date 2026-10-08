import { Activity } from 'lucide-react';
import styles from './Inspector.module.css';

function RunMetadataPanel({ failureSnapshot, traceTotal }) {
  return (
    <div className={styles.traceSummary}>
      <span><Activity size={12} aria-hidden="true" /> {traceTotal ?? 0} traces</span>
      {failureSnapshot ? <span>Failure snapshot loaded</span> : null}
    </div>
  );
}

export default RunMetadataPanel;
