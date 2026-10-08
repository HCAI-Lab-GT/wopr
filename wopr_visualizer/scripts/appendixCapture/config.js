import { join } from 'node:path';
import process from 'node:process';

export const HOST = '127.0.0.1';
export const VITE_PORT = 5174;
export const VIEWPORT = { width: 1600, height: 1000 };
export const ROOT = new URL('../..', import.meta.url).pathname;
export const REPO_ROOT = new URL('../../..', import.meta.url).pathname;
export const NUCLEAR_WAR_ROOT = join(REPO_ROOT, 'nuclear_war');
export const OUTPUT_DIR = join(ROOT, 'output', 'playwright', 'appendix-demo');
// Optional paper checkout. When WOPR_OVERLEAF_DIR is set, the screenshots are
// also copied into its figures/demo/ directory; otherwise they stay in
// OUTPUT_DIR only.
export const OVERLEAF_DIR = process.env.WOPR_OVERLEAF_DIR || null;
export const OVERLEAF_DEMO_DIR = OVERLEAF_DIR
  ? join(OVERLEAF_DIR, 'figures', 'demo')
  : null;

export const SCREENSHOTS = [
  {
    file: '01-replay-table-event-light.png',
    view: 'Replay',
    state: 'Sample replay, event 4, Event tab',
    caption: 'Replay workbench table view for a cards-enqueued event.',
  },
  {
    file: '02-population-timeline-light.png',
    view: 'Replay',
    state: 'Sample replay, event 4, population chart and timeline',
    caption: 'Population chart and event timeline for the same replay.',
  },
  {
    file: '03-agent-decision-trace-light.png',
    view: 'Replay',
    state: 'Trace fixture replay, event 1, Agent tab',
    caption: 'Decision-trace inspector showing the selected action context.',
  },
  {
    file: '04-conversation-press-light.png',
    view: 'Replay',
    state: 'Full-press demo replay, event 28, Conversation tab',
    caption: 'Conversation inspector showing public and private press messages.',
  },
  {
    file: '05-forensic-json-light.png',
    view: 'Replay',
    state: 'Full-press demo replay, event 28, Forensic mode',
    caption: 'Forensic inspector exposing replay JSON for audit.',
  },
  {
    file: '06-batch-analysis-light.png',
    view: 'Batch',
    state: 'Sample batch summary',
    caption: 'Batch analysis view for the bundled three-run sample.',
  },
  {
    file: '07-live-play-light.png',
    view: 'Live',
    state: 'Seed 42 local live session, controlled player_0',
    caption: 'Live workbench connected to the local rules API.',
  },
];

export function outputPath(file) {
  return join(OUTPUT_DIR, file);
}

export function overleafPath(file) {
  return join(OVERLEAF_DEMO_DIR, file);
}

export function manifestMarkdown() {
  const rows = SCREENSHOTS.map((item) => (
    `| ${item.file} | ${item.view} | ${item.state} | figures/demo/${item.file} | ${item.caption} |`
  ));
  return [
    '# Appendix Demo Screenshot Manifest',
    '',
    'Captured from the WOPR visualizer using the Paper theme.',
    '',
    'Regenerate with:',
    '',
    '```bash',
    'cd wopr_visualizer',
    'npm run capture:appendix',
    '```',
    '',
    '| Screenshot | View | Source state | Paper asset | Caption draft |',
    '| --- | --- | --- | --- | --- |',
    ...rows,
    '',
  ].join('\n');
}
