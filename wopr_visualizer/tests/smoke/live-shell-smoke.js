import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { createServer } from 'node:net';
import { chromium } from 'playwright';

const ROOT = new URL('../..', import.meta.url).pathname;
const NUCLEAR_WAR_ROOT = new URL('../../../nuclear_war', import.meta.url).pathname;
const HOST = '127.0.0.1';
const START_TIMEOUT_MS = 30000;
const VITE_PORT = 5174;
const delay = (ms) => new Promise((resolve) => { setTimeout(resolve, ms); });

async function main() {
  const livePort = await findUnusedPort();
  const liveBaseUrl = `http://${HOST}:${livePort}`;
  const viteBaseUrl = `http://${HOST}:${VITE_PORT}`;
  const liveServer = startProcess('uv', [
    'run', 'nuclear-war', 'live-server', '--host', HOST, '--port', String(livePort),
    '--seed', '42', '--players', '3', '--controlled', 'player_0',
  ], { cwd: NUCLEAR_WAR_ROOT });
  const viteServer = startProcess('npm', [
    'run', 'dev', '--', '--host', HOST, '--port', String(VITE_PORT), '--strictPort',
  ], { cwd: ROOT });

  try {
    await waitForEndpoint(`${liveBaseUrl}/session`, liveServer, 'Live API server', true);
    await waitForEndpoint(viteBaseUrl, viteServer, 'Vite dev server');
    const browser = await chromium.launch({ headless: true });
    try {
      const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
      await checkLiveShell(page, viteBaseUrl, liveBaseUrl);
      await page.close();
    } finally {
      await browser.close();
    }
    await assertArtifactsExport(liveBaseUrl);
  } finally {
    await Promise.all([stopProcess(viteServer), stopProcess(liveServer)]);
  }
}

async function checkLiveShell(page, viteBaseUrl, liveBaseUrl) {
  await page.goto(viteBaseUrl);
  await page.getByText('Replay workbench').waitFor();
  await page.getByRole('tab', { name: 'Live' }).click();
  await page.getByLabel('Live API URL').fill(liveBaseUrl);
  await page.getByRole('region', { name: 'Live workbench' }).waitFor();
  await page.getByLabel('Nuclear War table').waitFor();
  await page.getByRole('heading', { name: 'Pending decision' }).waitFor();
  await page.getByLabel('Legal actions').waitFor();

  for (let attempts = 0; attempts < 6; attempts += 1) {
    const stepAgentButton = page.getByRole('button', { name: 'Step agent' });
    if (await stepAgentButton.isVisible()) {
      const beforeAgentStep = await currentStateVersion(page);
      await stepAgentButton.click();
      await waitForStateVersionChange(page, beforeAgentStep);
      return;
    }
    const actionButtons = page.getByLabel('Legal actions').locator('button');
    if (await actionButtons.count() === 0) throw new Error('Live shell did not render legal action buttons.');
    const beforeAction = await currentStateVersion(page);
    await actionButtons.first().click();
    await waitForStateVersionChange(page, beforeAction);
  }
  throw new Error('Live shell did not expose Step agent after controlled-player decisions.');
}

async function currentStateVersion(page) {
  const text = await page.getByLabel('Live session metadata').textContent();
  const match = text?.match(/state\s+(\d+)/i);
  if (!match) throw new Error('Live shell did not expose a state version.');
  return Number(match[1]);
}

async function waitForStateVersionChange(page, previousVersion) {
  await page.waitForFunction((version) => {
    const text = document.querySelector('[aria-label="Live session metadata"]')?.textContent ?? '';
    const match = text.match(/state\s+(\d+)/i);
    return match !== null && Number(match[1]) !== version;
  }, previousVersion);
}

async function assertArtifactsExport(liveBaseUrl) {
  const response = await fetch(`${liveBaseUrl}/artifacts`);
  if (!response.ok) throw new Error(`/artifacts returned HTTP ${response.status}.`);
  const payload = await response.json();
  if (!Array.isArray(payload.replay?.actions) || payload.replay.actions.length === 0) {
    throw new Error('/artifacts did not include replay actions after live mutations.');
  }
}

async function waitForEndpoint(url, child, label, json = false) {
  const started = Date.now();
  while (Date.now() - started < START_TIMEOUT_MS) {
    if (child.exitCode !== null) {
      throw new Error(`${label} exited with code ${child.exitCode}.\nprocess output:\n${child.output}`);
    }
    try {
      const response = await fetch(url);
      if (response.ok) {
        if (json) await response.json();
        return;
      }
    } catch {
      await delay(250);
    }
  }
  throw new Error(`${label} did not start within 30 seconds.\nprocess output:\n${child.output}`);
}

function startProcess(command, args, options) {
  const child = spawn(command, args, { ...options, stdio: ['ignore', 'pipe', 'pipe'] });
  child.output = '';
  for (const stream of [child.stdout, child.stderr]) {
    stream.setEncoding('utf8');
    stream.on('data', (chunk) => { child.output += chunk; });
  }
  return child;
}

async function stopProcess(child) {
  if (child.exitCode !== null || child.signalCode !== null) return;
  const closed = once(child, 'close');
  child.kill('SIGTERM');
  const timedOut = await Promise.race([closed.then(() => false), delay(5000).then(() => true)]);
  if (timedOut && child.exitCode === null && child.signalCode === null) {
    child.kill('SIGKILL');
    await once(child, 'close');
  }
}

function findUnusedPort() {
  return new Promise((resolve, reject) => {
    const server = createServer();
    server.unref();
    server.on('error', reject);
    server.listen(0, HOST, () => {
      const address = server.address();
      const port = typeof address === 'object' && address !== null ? address.port : null;
      server.close(() => (port === null ? reject(new Error('No local port assigned.')) : resolve(port)));
    });
  });
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
