import { BrainCircuit, CheckCircle2, RotateCcw } from 'lucide-react';
import { formatSentenceLabel, formatPlayerId } from '../replay/replayFormatters.js';
import styles from './LiveDecisionPanel.module.css';

function LiveDecisionPanel({
  canStepAgent = false,
  canSubmitAction = true,
  decision,
  error = null,
  loading = false,
  submitting = false,
  onRefresh,
  onStepAgent,
  onSubmitAction,
}) {
  const pending = decision?.pending === true;
  const stateVersion = decision?.state_version;
  const hasStateVersion = Number.isFinite(stateVersion);
  const decisionActions = pending ? decision.legal_actions ?? [] : [];
  const legalActions = canSubmitAction ? decisionActions : [];
  const mutationDisabled = loading || submitting || !hasStateVersion;
  const refreshDisabled = loading || submitting;

  function handleRefresh() {
    onRefresh?.();
  }

  function handleStepAgent() {
    if (!hasStateVersion) return;
    onStepAgent?.(stateVersion);
  }

  return (
    <aside className={styles.panel} aria-label="Live decision controls">
      <header className={styles.header}>
        <div>
          <p className={styles.eyebrow}>Live controls</p>
          <h2>Pending decision</h2>
        </div>
        {onRefresh ? (
          <button className={styles.secondaryButton} disabled={refreshDisabled} onClick={handleRefresh} type="button">
            <RotateCcw size={16} aria-hidden="true" />
            Refresh
          </button>
        ) : null}
      </header>
      {error ? <StructuredError error={error} /> : null}
      {pending ? (
        <>
          <dl className={styles.summaryGrid}>
            <Metric label="Owner" value={formatPlayerId(decision.agent_id)} />
            <Metric label="Decision type" value={formatSentenceLabel(decision.decision_type)} />
            <Metric label="State version" value={stateVersion} />
            <Metric label="Legal actions" value={decisionActions.length} />
          </dl>
          {canStepAgent ? <div className={styles.controlRow}>
            <button
              className={styles.secondaryButton}
              disabled={mutationDisabled}
              onClick={handleStepAgent}
              type="button"
            >
              <BrainCircuit size={16} aria-hidden="true" />
              Step agent
            </button>
          </div> : null}
          {canSubmitAction ? (
            <section className={styles.actions} aria-label="Legal actions">
              {legalActions.map((action) => (
                <LegalActionButton
                  action={action}
                  disabled={mutationDisabled}
                  key={action.action_id}
                  onSubmitAction={onSubmitAction}
                  stateVersion={stateVersion}
                />
              ))}
            </section>
          ) : (
            <p className={styles.emptyState}>Manual action selection is unavailable for this seat.</p>
          )}
        </>
      ) : (
        <p className={styles.emptyState}>No pending decision.</p>
      )}
    </aside>
  );
}

function LegalActionButton({ action, disabled, onSubmitAction, stateVersion }) {
  function handleClick() {
    if (!Number.isFinite(stateVersion)) return;
    onSubmitAction?.(action.action_id, stateVersion);
  }

  return (
    <button className={styles.actionButton} disabled={disabled} onClick={handleClick} type="button">
      <CheckCircle2 size={16} aria-hidden="true" />
      <span>{action.label ?? action.action_id}</span>
    </button>
  );
}

function Metric({ label, value }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value ?? 'unknown'}</dd>
    </div>
  );
}

function StructuredError({ error }) {
  const code = error?.code ?? error?.name ?? 'request_error';
  const message = error?.message ?? 'Live API request failed.';
  const status = error?.status === undefined ? null : `HTTP ${error.status}`;

  return (
    <section className={styles.errorPanel} role="alert" aria-label="Live API error">
      <p className={styles.errorCode}>{code}</p>
      <p>{message}</p>
      {status ? <p className={styles.errorStatus}>{status}</p> : null}
    </section>
  );
}

export default LiveDecisionPanel;
