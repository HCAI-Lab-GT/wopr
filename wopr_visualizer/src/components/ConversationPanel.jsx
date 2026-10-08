import { MessagesSquare } from 'lucide-react';
import styles from './Inspector.module.css';
import panelStyles from './InspectorPanel.module.css';

function ConversationPanel({ conversationArtifacts }) {
  const messages = conversationArtifacts?.messages ?? [];
  if (messages.length === 0) {
    return <div className={styles.emptyPanel}>No press messages in this replay.</div>;
  }
  return (
    <div className={styles.detailPanel}>
      <div className={panelStyles.panelTitleRow}>
        <MessagesSquare size={18} aria-hidden="true" />
        <h3>Conversation</h3>
      </div>
      <div className={panelStyles.messageList}>
        {messages.map((message) => (
          <article className={panelStyles.messageRow} key={message.id}>
            <p className={styles.label}>Turn {message.turn} · {message.visibility}</p>
            <p>{channelLine(message)}</p>
            <p>{message.text}</p>
            {message.commitment ? <CommitmentBadge commitment={message.commitment} /> : null}
          </article>
        ))}
      </div>
    </div>
  );
}

function channelLine(message) {
  if (message.visibility === 'private') {
    return `${message.speakerLabel} whispered to ${message.recipientLabel ?? message.audienceLabel}`;
  }
  return `${message.speakerLabel} to ${message.audienceLabel}`;
}

function CommitmentBadge({ commitment }) {
  const parts = [commitment.kind];
  if (commitment.target_round != null) {
    parts.push(`round ${commitment.target_round}`);
  }
  return (
    <p className={styles.label} data-testid="commitment-badge">
      Commitment: {parts.join(' · ')}
    </p>
  );
}

export default ConversationPanel;
