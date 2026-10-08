import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { chromium } from 'playwright';
import { traceArtifactPayload, traceReplayPayload, unsupportedReplayPayload } from '../../src/test/replayFixtures.js';

const ROOT = new URL('../..', import.meta.url).pathname;
const PORT = 5174;
const BASE_URL = `http://127.0.0.1:${PORT}`;
const VIEWPORTS = [
  { name: 'desktop', width: 1280, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
];
const FIRST_TURN_TWO_FRAME = 28;

async function main() {
  const server = spawn('npm', ['run', 'dev', '--', '--host', '127.0.0.1', '--port', String(PORT)], {
    cwd: ROOT,
    stdio: ['ignore', 'pipe', 'pipe'],
  });
  try {
    await waitForServer();
    await runBrowserChecks();
  } finally {
    server.kill('SIGTERM');
  }
}

async function waitForServer() {
  const started = Date.now();
  while (Date.now() - started < 30000) {
    try {
      const response = await fetch(BASE_URL);
      if (response.ok) return;
    } catch {
      await delay(250);
    }
  }
  throw new Error('Vite dev server did not start within 30 seconds.');
}

async function runBrowserChecks() {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const viewport of VIEWPORTS) {
      const page = await browser.newPage({ viewport });
      await checkWorkbench(page, viewport.name);
      await page.close();
    }
  } finally {
    await browser.close();
  }
}

async function checkWorkbench(page, viewportName) {
  await page.goto(BASE_URL);
  await page.getByText('Replay workbench').waitFor();
  await page.getByLabel('Nuclear War table').waitFor();
  await page.getByText('Current event').waitFor();
  await setRangeValue(page, 4);
  await page.getByText(/cards enqueued/i).first().waitFor();
  await captureTableScreenshot(page, viewportName);
  await assertTableSurfaceVisible(page, viewportName);
  await page.getByRole('button', { name: 'Agent' }).click();
  await page.getByText('No related decision trace for this event.').waitFor();
  await page.getByRole('button', { name: 'Conversation' }).click();
  await page.getByText('No press messages in this replay.').waitFor();
  await page.getByRole('button', { name: 'Forensic' }).click();
  await page.getByText('Event JSON').waitFor();

  const traceReplayPath = await writeTraceReplay();
  const traceArtifactPath = await writeTraceArtifact();
  await page.getByLabel('Load replay').setInputFiles(traceReplayPath);
  await page.getByLabel('Load traces').setInputFiles(traceArtifactPath);
  await setRangeValue(page, 1);
  await page.getByRole('button', { name: 'Agent' }).click();
  await page.getByText('Agent decision', { exact: true }).waitFor();
  await page.getByText('player_0:draw').waitFor();

  const unsupportedPath = await writeUnsupportedReplay();
  await page.getByLabel('Load replay').setInputFiles(unsupportedPath);
  await setRangeValue(page, 1);
  await page.getByText('No reducer handler for this event.').waitFor();
  await page.getByRole('button', { name: 'Forensic' }).click();
  await page.getByText('Event JSON').waitFor();

  const pressReplayPath = await writePressReplay();
  const pressArtifactPath = await writePressArtifact();
  await page.getByLabel('Load replay').setInputFiles(pressReplayPath);
  await page.getByLabel('Load press').setInputFiles(pressArtifactPath);
  await setRangeValue(page, FIRST_TURN_TWO_FRAME);
  await page.getByRole('button', { name: 'Conversation' }).click();
  await page.getByText(/press messages/i).first().waitFor();
  await page.getByText('Public').first().waitFor();

  const multiTurnReplayPath = await writeMultiTurnReplay();
  const multiTurnPressPath = await writeMultiTurnPress();
  await page.getByLabel('Load replay').setInputFiles(multiTurnReplayPath);
  await page.getByLabel('Load press').setInputFiles(multiTurnPressPath);
  await setRangeValue(page, FIRST_TURN_TWO_FRAME);
  await page.getByRole('button', { name: 'Conversation' }).click();
  await page.getByText(/press messages/i).first().waitFor();
  await page.getByText('Public').first().waitFor();

  const fullPressReplayPath = await writeFullPressReplay();
  const fullPressPressPath = await writeFullPressPress();
  await page.getByLabel('Load replay').setInputFiles(fullPressReplayPath);
  await page.getByLabel('Load press').setInputFiles(fullPressPressPath);
  await setRangeValue(page, FIRST_TURN_TWO_FRAME);
  await page.getByRole('button', { name: 'Conversation' }).click();
  await page.getByText(/press messages/i).first().waitFor();
  await page.getByText('whispered to').first().waitFor();
}

async function captureTableScreenshot(page, viewportName) {
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: join(tmpdir(), `wopr-replay-workbench-${viewportName}.png`) });
}

async function assertTableSurfaceVisible(page, viewportName) {
  const tableBox = await page.getByLabel('Player tableaus').boundingBox();
  if (!tableBox || tableBox.width < 300 || tableBox.height < 220) {
    throw new Error(`Player tableaus are not visibly rendered in ${viewportName}.`);
  }
}

async function setRangeValue(page, value) {
  await page.getByLabel('Select event').evaluate((input, nextValue) => {
    const valueSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    valueSetter.call(input, String(nextValue));
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }, value);
}

async function writeUnsupportedReplay() {
  const path = join(tmpdir(), 'wopr-unsupported-replay.json');
  await writeFile(path, JSON.stringify(unsupportedReplayPayload()), 'utf8');
  return path;
}

async function writeTraceReplay() {
  const path = join(tmpdir(), 'wopr-trace-replay.json');
  await writeFile(path, JSON.stringify(traceReplayPayload()), 'utf8');
  return path;
}

async function writeTraceArtifact() {
  const path = join(tmpdir(), 'wopr-trace-replay.traces.json');
  await writeFile(path, JSON.stringify(traceArtifactPayload()), 'utf8');
  return path;
}

async function writePressReplay() {
  const source = join(ROOT, 'src', 'data', 'pressLightDemo', 'replay.json');
  const path = join(tmpdir(), 'wopr-press-replay.json');
  await writeFile(path, await readFile(source, 'utf8'), 'utf8');
  return path;
}

async function writePressArtifact() {
  const source = join(ROOT, 'src', 'data', 'pressLightDemo', 'press_traces.json');
  const path = join(tmpdir(), 'wopr-press-traces.json');
  await writeFile(path, await readFile(source, 'utf8'), 'utf8');
  return path;
}

async function writeMultiTurnReplay() {
  const source = join(ROOT, 'src', 'data', 'multiTurnDemo', 'replay.json');
  const path = join(tmpdir(), 'wopr-multiturn-replay.json');
  await writeFile(path, await readFile(source, 'utf8'), 'utf8');
  return path;
}

async function writeMultiTurnPress() {
  const source = join(ROOT, 'src', 'data', 'multiTurnDemo', 'press_traces.json');
  const path = join(tmpdir(), 'wopr-multiturn-press.json');
  await writeFile(path, await readFile(source, 'utf8'), 'utf8');
  return path;
}

async function writeFullPressReplay() {
  const source = join(ROOT, 'src', 'data', 'fullPressDemo', 'replay.json');
  const path = join(tmpdir(), 'wopr-fullpress-replay.json');
  await writeFile(path, await readFile(source, 'utf8'), 'utf8');
  return path;
}

async function writeFullPressPress() {
  const source = join(ROOT, 'src', 'data', 'fullPressDemo', 'press_traces.json');
  const path = join(tmpdir(), 'wopr-fullpress-press.json');
  await writeFile(path, await readFile(source, 'utf8'), 'utf8');
  return path;
}

function delay(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
