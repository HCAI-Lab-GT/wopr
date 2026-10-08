import { AlertTriangle, ScrollText } from 'lucide-react';
import { buildEventStory } from '../replay/eventStories.js';
import styles from './Inspector.module.css';
import panelStyles from './InspectorPanel.module.css';

function EventStoryPanel({ frame }) {
  const story = buildEventStory(frame);
  return (
    <div className={styles.detailPanel}>
      <div className={panelStyles.panelTitleRow}>
        <ScrollText size={18} aria-hidden="true" />
        <h3>{story.title}</h3>
      </div>
      <p>{story.body}</p>
      <section>
        <p className={styles.label}>Consequences</p>
        <ul className={panelStyles.cleanList}>
          {story.consequences.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </section>
      {story.warnings.length > 0 ? (
        <section>
          <p className={styles.label}>Warnings</p>
          <ul className={panelStyles.cleanList}>
            {story.warnings.map((warning) => (
              <li className={panelStyles.warningItem} key={warning}>
                <AlertTriangle size={14} aria-hidden="true" />
                {warning}
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}

export default EventStoryPanel;
