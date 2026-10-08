import process from 'node:process';
import { copyFile, mkdir, writeFile } from 'node:fs/promises';
import { chromium } from 'playwright';
import {
  HOST,
  NUCLEAR_WAR_ROOT,
  OUTPUT_DIR,
  OVERLEAF_DEMO_DIR,
  ROOT,
  SCREENSHOTS,
  VITE_PORT,
  VIEWPORT,
  manifestMarkdown,
  outputPath,
  overleafPath,
} from './appendixCapture/config.js';
import {
  findUnusedPort,
  startProcess,
  stopProcess,
  waitForEndpoint,
} from './appendixCapture/processes.js';
import {
  capturePopulationTimeline,
  captureViewport,
  loadFullPressDemo,
  loadTraceFixture,
  openWorkbench,
  setRangeValue,
  showConversation,
  showForensic,
  showLiveView,
  showSampleBatch,
} from './appendixCapture/pageActions.js';

async function main() {
  await mkdir(OUTPUT_DIR, { recursive: true });
  if (OVERLEAF_DEMO_DIR) await mkdir(OVERLEAF_DEMO_DIR, { recursive: true });
  const livePort = await findUnusedPort(HOST);
  const viteBaseUrl = `http://${HOST}:${VITE_PORT}`;
  const liveBaseUrl = `http://${HOST}:${livePort}`;
  const viteServer = startVite();
  const liveServer = startLiveApi(livePort);

  try {
    await waitForEndpoint(viteBaseUrl, viteServer, 'Vite dev server');
    await waitForEndpoint(`${liveBaseUrl}/session`, liveServer, 'Live API server', true);
    await runCapture(viteBaseUrl, liveBaseUrl);
    if (OVERLEAF_DEMO_DIR) await copyScreenshotsToOverleaf();
    await writeRecords();
  } finally {
    await Promise.all([stopProcess(viteServer), stopProcess(liveServer)]);
  }
}

function startVite() {
  return startProcess('npm', [
    'run', 'dev', '--', '--host', HOST, '--port', String(VITE_PORT), '--strictPort',
  ], { cwd: ROOT });
}

function startLiveApi(port) {
  return startProcess('uv', [
    'run', 'nuclear-war', 'live-server',
    '--host', HOST,
    '--port', String(port),
    '--seed', '42',
    '--players', '3',
    '--controlled', 'player_0',
  ], { cwd: NUCLEAR_WAR_ROOT });
}

async function runCapture(viteBaseUrl, liveBaseUrl) {
  const browser = await chromium.launch({ headless: true });
  try {
    const page = await browser.newPage({ deviceScaleFactor: 2, viewport: VIEWPORT });
    await openWorkbench(page, viteBaseUrl);
    await setRangeValue(page, 4);
    await page.getByText(/cards enqueued/i).first().waitFor();
    await captureViewport(page, SCREENSHOTS[0].file);
    await capturePopulationTimeline(page, SCREENSHOTS[1].file);
    await loadTraceFixture(page);
    await captureViewport(page, SCREENSHOTS[2].file);
    await loadFullPressDemo(page);
    await showConversation(page);
    await captureViewport(page, SCREENSHOTS[3].file);
    await showForensic(page);
    await captureViewport(page, SCREENSHOTS[4].file);
    await showSampleBatch(page);
    await captureViewport(page, SCREENSHOTS[5].file);
    await showLiveView(page, liveBaseUrl);
    await captureViewport(page, SCREENSHOTS[6].file);
    await page.close();
  } finally {
    await browser.close();
  }
}

async function copyScreenshotsToOverleaf() {
  for (const item of SCREENSHOTS) {
    await copyFile(outputPath(item.file), overleafPath(item.file));
  }
}

async function writeRecords() {
  await writeFile(`${OUTPUT_DIR}/manifest.md`, manifestMarkdown(), 'utf8');
  if (OVERLEAF_DEMO_DIR) {
    await writeFile(`${OVERLEAF_DEMO_DIR}/README.md`, overleafReadme(), 'utf8');
  }
}

function overleafReadme() {
  return [
    '# Demo Figure Assets',
    '',
    'These PNG files are paper-facing copies of the visualizer screenshots',
    'captured under `wopr_visualizer/output/playwright/appendix-demo/`.',
    '',
    'Regenerate from the repository root with:',
    '',
    '```bash',
    'cd wopr_visualizer',
    'npm run capture:appendix',
    '```',
    '',
    'LaTeX should reference only `figures/demo/...` paths. The sibling',
    '`wopr_visualizer/output/...` path is a capture staging area and is not',
    'visible to Overleaf.',
    '',
  ].join('\n');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
