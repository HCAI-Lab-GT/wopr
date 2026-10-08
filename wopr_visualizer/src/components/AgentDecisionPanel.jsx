import { BrainCircuit, CheckCircle2, FileText, ListChecks, RadioTower } from 'lucide-react';
import { summarizeDecisionTrace } from '../replay/decisionSummaries.js';
import styles from './Inspector.module.css';
import panelStyles from './InspectorPanel.module.css';

function AgentDecisionPanel({ frame }) {
  const summary = summarizeDecisionTrace(frame.decisionTrace, frame.relatedAction);
  if (!summary) {
    return <div className={styles.emptyPanel}>No related decision trace for this event.</div>;
  }
  return (
    <div className={styles.detailPanel}>
      <div className={panelStyles.panelTitleRow}>
        <BrainCircuit size={18} aria-hidden="true" />
        <h3>Agent decision</h3>
      </div>
      <div className={panelStyles.summaryGrid}>
        <Metric label="Selected action" value={summary.selectedActionId} />
        <Metric label="Action label" value={summary.selectedActionLabel} />
        <Metric label="Decision type" value={summary.decisionType} />
        <Metric label="Validation" value={summary.validationStatus} />
      </div>
      <IconSection icon={<ListChecks size={16} />} label="Legal options">
        {summary.legalOptionGroups.map((group) => (
          <div className={panelStyles.optionGroup} key={group.family}>
            <p>{group.family}</p>
            {group.options.map((option) => (
              <span className={panelStyles.chip} key={option.actionId}>{option.label}</span>
            ))}
          </div>
        ))}
      </IconSection>
      <IconSection icon={<CheckCircle2 size={16} />} label="Validation errors">
        {summary.validationErrors.length > 0 ? (
          summary.validationErrors.map((error) => <p className={styles.warningPill} key={error}>{error}</p>)
        ) : (
          <p>No validation errors recorded.</p>
        )}
      </IconSection>
      <IconSection icon={<RadioTower size={16} />} label="Provider">
        <div className={styles.traceSummary}>
          {[summary.provider.label, summary.provider.model, tokenLabel(summary.provider.usage)]
            .filter(Boolean)
            .map((value) => <span key={value}>{value}</span>)}
        </div>
      </IconSection>
      <IconSection icon={<FileText size={16} />} label="Prompt and response">
        <p className={panelStyles.previewText}>{summary.promptPreview}</p>
        <p className={panelStyles.previewText}>{summary.responsePreview}</p>
      </IconSection>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div>
      <p className={styles.label}>{label}</p>
      <p>{value ?? 'Not recorded'}</p>
    </div>
  );
}

function IconSection({ icon, label, children }) {
  return (
    <section>
      <p className={panelStyles.sectionLabel}>{icon}{label}</p>
      {children}
    </section>
  );
}

function tokenLabel(usage) {
  return typeof usage?.total_tokens === 'number' ? `${usage.total_tokens} tokens` : null;
}

export default AgentDecisionPanel;
