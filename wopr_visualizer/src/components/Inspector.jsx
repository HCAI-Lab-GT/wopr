import { FileJson, Gamepad2 } from 'lucide-react';
import { formatSentenceLabel } from '../replay/replayFormatters.js';
import AgentDecisionPanel from './AgentDecisionPanel.jsx';
import ConversationPanel from './ConversationPanel.jsx';
import EventStoryPanel from './EventStoryPanel.jsx';
import ForensicPanel from './ForensicPanel.jsx';
import styles from './Inspector.module.css';

const GAME_TABS = ['Event', 'Agent', 'Conversation'];
const MODES = ['Game', 'Forensic'];

function Inspector({
  frame,
  events,
  selectedIndex,
  onSelectIndex,
  inspectorMode = 'Game',
  gameTab = 'Event',
  onInspectorModeChange,
  onGameTabChange,
  conversationArtifacts,
  failureSnapshot,
}) {
  return (
    <aside className={styles.inspector} aria-label="Replay inspector">
      <div className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Inspector</p>
          <h2>{formatSentenceLabel(frame.event?.event_type)}</h2>
        </div>
        {frame.warnings.length > 0 ? <span className={styles.warningPill}>Warning</span> : null}
      </div>
      <ButtonRow
        active={inspectorMode}
        items={MODES}
        label="Inspector mode"
        onSelect={onInspectorModeChange}
      />
      {inspectorMode === 'Game' ? (
        <ButtonRow active={gameTab} items={GAME_TABS} label="Game tabs" onSelect={onGameTabChange} />
      ) : null}
      <div className={styles.inspectorBody}>
        {renderPanel({
          conversationArtifacts,
          events,
          failureSnapshot,
          frame,
          gameTab,
          inspectorMode,
          onSelectIndex,
          selectedIndex,
        })}
      </div>
    </aside>
  );
}

function ButtonRow({ active, items, label, onSelect }) {
  return (
    <div className={styles.tabs} role="tablist" aria-label={label}>
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
      aria-selected={active}
      className={`${styles.tab} ${active ? styles.tabActive : ''}`}
      onClick={handleClick}
      role="tab"
      type="button"
    >
      {item === 'Game' ? <Gamepad2 size={14} aria-hidden="true" /> : null}
      {item === 'Forensic' ? <FileJson size={14} aria-hidden="true" /> : null}
      {item}
    </button>
  );
}

function renderPanel({ conversationArtifacts, failureSnapshot, frame, gameTab, inspectorMode }) {
  if (inspectorMode === 'Forensic') {
    return <ForensicPanel failureSnapshot={failureSnapshot} frame={frame} />;
  }
  if (gameTab === 'Agent') {
    return <AgentDecisionPanel frame={frame} />;
  }
  if (gameTab === 'Conversation') {
    return <ConversationPanel conversationArtifacts={conversationArtifacts} frame={frame} />;
  }
  return <EventStoryPanel frame={frame} />;
}

export default Inspector;
