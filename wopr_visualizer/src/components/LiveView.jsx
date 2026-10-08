import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { createLiveClient } from '../live/liveClient.js';
import { buildLiveTableViewModel } from '../live/liveTableViewModel.js';
import { formatSentenceLabel } from '../replay/replayFormatters.js';
import GameTable from './GameTable.jsx';
import LiveDecisionPanel from './LiveDecisionPanel.jsx';
import styles from './LiveView.module.css';

const DEFAULT_API_URL = 'http://127.0.0.1:8765';

function LiveView({
  apiUrl = DEFAULT_API_URL,
  client = null,
  fetchImpl,
  gameTab,
  inspectorMode,
  onGameTabChange,
  onInspectorModeChange,
}) {
  const liveClient = useMemo(() => client ?? createLiveClient(apiUrl, fetchImpl), [apiUrl, client, fetchImpl]);
  const [session, setSession] = useState(null);
  const [state, setState] = useState(null);
  const [decision, setDecision] = useState(null);
  const [selectedContext, setSelectedContext] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const mountedRef = useRef(false);

  const table = useMemo(() => {
    if (!state || !decision) return null;
    return buildLiveTableViewModel({ state, decision });
  }, [decision, state]);
  const canStepAgent = decision?.pending === true && (session?.agent_players ?? []).includes(decision.agent_id);
  const canSubmitAction = decision?.pending === true && (session?.controlled_players ?? []).includes(decision.agent_id);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const refreshAll = useCallback(async () => {
    if (submitting) return;
    setLoading(true);
    setError(null);
    try {
      const [nextSession, nextState, nextDecision] = await Promise.all([
        liveClient.getSession(),
        liveClient.getState(),
        liveClient.getDecision(),
      ]);
      if (!mountedRef.current) return;
      setSession(nextSession);
      setState(nextState);
      setDecision(nextDecision);
    } catch (nextError) {
      if (!mountedRef.current) return;
      setError(nextError);
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [liveClient, submitting]);

  const refreshStateAndDecision = useCallback(async () => {
    const [nextState, nextDecision] = await Promise.all([liveClient.getState(), liveClient.getDecision()]);
    if (!mountedRef.current) return;
    setState(nextState);
    setDecision(nextDecision);
  }, [liveClient]);

  useEffect(() => {
    let active = true;

    async function connect() {
      setLoading(true);
      setError(null);
      try {
        const [nextSession, nextState, nextDecision] = await Promise.all([
          liveClient.getSession(),
          liveClient.getState(),
          liveClient.getDecision(),
        ]);
        if (!active) return;
        setSession(nextSession);
        setState(nextState);
        setDecision(nextDecision);
      } catch (nextError) {
        if (active) {
          setError(nextError);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    connect();
    return () => {
      active = false;
    };
  }, [liveClient]);

  async function handleSubmitAction(actionId, stateVersion) {
    setSubmitting(true);
    setError(null);
    try {
      await liveClient.submitDecision(actionId, stateVersion);
      await refreshStateAndDecision();
    } catch (nextError) {
      if (!mountedRef.current) return;
      setError(nextError);
    } finally {
      if (mountedRef.current) {
        setSubmitting(false);
      }
    }
  }

  async function handleStepAgent(stateVersion) {
    setSubmitting(true);
    setError(null);
    try {
      await liveClient.stepAgent(stateVersion);
      await refreshStateAndDecision();
    } catch (nextError) {
      if (!mountedRef.current) return;
      setError(nextError);
    } finally {
      if (mountedRef.current) {
        setSubmitting(false);
      }
    }
  }

  function handleSelectContext(nextSelectedContext) {
    setSelectedContext(nextSelectedContext);
  }

  return (
    <section className={styles.liveView} aria-label="Live workbench">
      <header className={styles.statusBar}>
        <div>
          <p className={styles.eyebrow}>Live session</p>
          <h1>{session?.session_id ?? 'Not connected'}</h1>
        </div>
        <div className={styles.statusLine} aria-label="Live session metadata">
          {session ? <span>Seed {session.seed}</span> : null}
          {session ? <span>{formatSentenceLabel(session.status)}</span> : null}
          {state ? <span>State {state.state_version}</span> : null}
          {loading ? <span>Loading</span> : null}
        </div>
      </header>
      <div className={styles.workspace}>
        {table ? (
          <GameTable
            gameTab={gameTab}
            inspectorMode={inspectorMode}
            onGameTabChange={onGameTabChange}
            onInspectorModeChange={onInspectorModeChange}
            onSelectContext={handleSelectContext}
            selectedContext={selectedContext}
            table={table}
          />
        ) : (
          <div className={styles.emptyTable}>No live table state loaded.</div>
        )}
        <LiveDecisionPanel
          decision={decision}
          error={error}
          canStepAgent={canStepAgent}
          canSubmitAction={canSubmitAction}
          loading={loading}
          onRefresh={refreshAll}
          onStepAgent={handleStepAgent}
          onSubmitAction={handleSubmitAction}
          submitting={submitting}
        />
      </div>
    </section>
  );
}

export default LiveView;
