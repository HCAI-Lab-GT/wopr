import { FileJson } from 'lucide-react';
import styles from './Inspector.module.css';
import panelStyles from './InspectorPanel.module.css';

function ForensicPanel({ frame, failureSnapshot }) {
  const trace = frame.decisionTrace;
  return (
    <div className={styles.detailPanel}>
      <div className={panelStyles.panelTitleRow}>
        <FileJson size={18} aria-hidden="true" />
        <h3>Forensic data</h3>
      </div>
      <JsonSection label="Event JSON" value={frame.event ?? { type: 'initial_state' }} />
      <JsonSection label="Related action JSON" value={frame.relatedAction ?? null} />
      <JsonSection label="Decision trace JSON" value={trace ?? null} />
      {trace ? (
        <>
          <JsonSection label="Prompt history" value={trace.prompts ?? [trace.prompt]} />
          <JsonSection label="Raw response history" value={trace.raw_responses ?? [trace.raw_response]} />
          <JsonSection label="Parse result" value={trace.parse_result} />
        </>
      ) : null}
      {failureSnapshot ? <JsonSection label="Failure snapshot" value={failureSnapshot} /> : null}
    </div>
  );
}

function JsonSection({ label, value }) {
  return (
    <section>
      <p className={styles.label}>{label}</p>
      <pre className={styles.jsonBlock}>{JSON.stringify(value, null, 2)}</pre>
    </section>
  );
}

export default ForensicPanel;
