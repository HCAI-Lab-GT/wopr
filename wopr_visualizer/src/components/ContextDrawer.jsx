import { FileJson, Gamepad2 } from 'lucide-react';
import { formatSentenceLabel } from '../replay/replayFormatters.js';
import AgentDecisionPanel from './AgentDecisionPanel.jsx';
import ConversationPanel from './ConversationPanel.jsx';
import EventStoryPanel from './EventStoryPanel.jsx';
import ForensicPanel from './ForensicPanel.jsx';
import styles from './ContextDrawer.module.css';

const GAME_TABS = ['Event', 'Agent', 'Conversation'];
const INSPECTOR_MODES = ['Game', 'Forensic'];

function ContextDrawer({
  context,
  inspectorMode = 'Game',
  gameTab = 'Event',
  selectedContext = null,
  onInspectorModeChange,
  onGameTabChange,
}) {
  const activeMode = INSPECTOR_MODES.includes(inspectorMode) ? inspectorMode : 'Game';
  const activeTab = GAME_TABS.includes(gameTab) ? gameTab : 'Event';
  const frame = contextFrame(context);
  const warnings = context?.warnings ?? [];

  return (
    <aside className={styles.drawer} aria-label="Table context">
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Context</p>
          <h2>{formatSentenceLabel(frame.event?.event_type)}</h2>
        </div>
        {warnings.length > 0 ? <span className={styles.warningPill}>Warning</span> : null}
      </div>
      <ButtonRow
        active={activeMode}
        items={INSPECTOR_MODES}
        label="Context mode"
        onSelect={onInspectorModeChange}
      />
      {activeMode === 'Game' ? (
        <ButtonRow active={activeTab} items={GAME_TABS} label="Game context tabs" onSelect={onGameTabChange} />
      ) : null}
      <div className={styles.drawerBody}>
        <SelectedTableSummary selectedContext={selectedContext} />
        {renderContextPanel({
          activeMode,
          activeTab,
          context,
          frame,
        })}
      </div>
    </aside>
  );
}

function SelectedTableSummary({ selectedContext }) {
  if (!selectedContext) return null;
  if (selectedContext.kind === 'player') {
    return <SelectedPlayerSummary player={selectedContext.player} />;
  }
  if (selectedContext.kind === 'queue') {
    return <SelectedQueueSummary player={selectedContext.player} slot={selectedContext.slot} />;
  }
  return null;
}

function SelectedPlayerSummary({ player }) {
  return (
    <section aria-label="Selected table object" aria-live="polite" className={styles.selectionSummary}>
      <p className={styles.eyebrow}>Selected table object</p>
      <h3>{player.label}</h3>
      <dl className={styles.selectionGrid}>
        <SelectionFact label="Population" value={player.populationLabel} />
        <SelectionFact label="Status" value={player.aliveLabel} />
        <SelectionFact label="War" value={player.warLabel} />
        <SelectionFact label="Queue" value={queueSummary(player.queue)} />
      </dl>
    </section>
  );
}

function SelectedQueueSummary({ player, slot }) {
  const cardLabel = slot.empty ? 'Empty' : slot.label;
  const heading = `${player.label} queue slot ${slot.index + 1}`;
  const slotLabel = `Slot ${slot.index + 1}`;

  return (
    <section aria-label="Selected table object" aria-live="polite" className={styles.selectionSummary}>
      <p className={styles.eyebrow}>Selected table object</p>
      <h3>{heading}</h3>
      <dl className={styles.selectionGrid}>
        <SelectionFact label="Player" value={player.label} />
        <SelectionFact label="Slot" value={slotLabel} />
        <SelectionFact label="Card" value={cardLabel} />
        <SelectionFact label="State" value={slot.empty ? 'Empty' : 'Occupied'} />
      </dl>
    </section>
  );
}

function SelectionFact({ label, value }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

function ButtonRow({ active, items, label, onSelect }) {
  return (
    <div className={styles.tabs} role="group" aria-label={label}>
      {items.map((item) => (
        <ModeButton active={active === item} item={item} key={item} onSelect={onSelect} />
      ))}
    </div>
  );
}

function ModeButton({ active, item, onSelect }) {
  function handleClick() {
    onSelect?.(item);
  }

  return (
    <button
      aria-pressed={active}
      className={`${styles.tab} ${active ? styles.tabActive : ''}`}
      onClick={handleClick}
      type="button"
    >
      {item === 'Game' ? <Gamepad2 size={14} aria-hidden="true" /> : null}
      {item === 'Forensic' ? <FileJson size={14} aria-hidden="true" /> : null}
      {item}
    </button>
  );
}

function renderContextPanel({ activeMode, activeTab, context, frame }) {
  if (activeMode === 'Forensic') {
    return <ForensicPanel failureSnapshot={context?.failureSnapshot ?? null} frame={frame} />;
  }
  if (activeTab === 'Agent') {
    return <AgentDecisionPanel frame={frame} />;
  }
  if (activeTab === 'Conversation') {
    return <ConversationPanel conversationArtifacts={conversationArtifacts(context)} frame={frame} />;
  }
  return <EventStoryPanel frame={frame} />;
}

function contextFrame(context) {
  return {
    ...(context?.frame ?? {}),
    decisionTrace: context?.decisionTrace ?? context?.frame?.decisionTrace ?? null,
    relatedAction: context?.relatedAction ?? context?.frame?.relatedAction ?? null,
    warnings: context?.frame?.warnings ?? [],
  };
}

function conversationArtifacts(context) {
  return {
    source: context?.pressMessages?.length ? 'turn' : 'none',
    messages: context?.pressMessages ?? [],
  };
}

function queueSummary(queue) {
  return queue.map((slot) => slot.cardId || `Slot ${slot.index + 1} empty`).join(', ');
}

export default ContextDrawer;
