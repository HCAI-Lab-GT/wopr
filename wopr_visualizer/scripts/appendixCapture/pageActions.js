import { Buffer } from 'node:buffer';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { traceArtifactPayload, traceReplayPayload } from '../../src/test/replayFixtures.js';
import { outputPath, ROOT } from './config.js';

export async function openWorkbench(page, viteBaseUrl) {
  await page.goto(viteBaseUrl);
  await page.getByText('Replay workbench').waitFor();
  await setPaperTheme(page);
}

export async function setPaperTheme(page) {
  await page.getByRole('button', { name: 'Paper' }).click();
  await page.locator('[data-theme="paper"]').waitFor();
}

export async function captureViewport(page, file) {
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({ path: outputPath(file) });
}

export async function capturePopulationTimeline(page, file) {
  await page.evaluate(() => {
    const header = document.querySelector('main > header');
    const table = document.querySelector('[aria-label="Nuclear War table"]');
    const workspace = table?.parentElement;
    for (const element of [header, workspace]) {
      if (element instanceof HTMLElement) {
        element.dataset.captureDisplay = element.style.display;
        element.style.display = 'none';
      }
    }
    window.scrollTo(0, 0);
  });
  try {
    await page.getByLabel('Population chart').waitFor();
    await page.getByLabel('Event timeline').waitFor();
    await page.screenshot({ path: outputPath(file), fullPage: true });
  } finally {
    await page.evaluate(() => {
      for (const element of document.querySelectorAll('[data-capture-display]')) {
        element.style.display = element.dataset.captureDisplay ?? '';
        delete element.dataset.captureDisplay;
      }
    });
  }
}

export async function setRangeValue(page, value) {
  await page.getByLabel('Select event').evaluate((input, nextValue) => {
    const valueSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
    valueSetter.call(input, String(nextValue));
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('change', { bubbles: true }));
  }, value);
}

export async function loadTraceFixture(page) {
  await page.getByLabel('Load replay').setInputFiles(filePayload(
    'appendix-trace-replay.json',
    traceReplayPayload(),
  ));
  await page.getByLabel('Load traces').setInputFiles(filePayload(
    'appendix-trace-replay.traces.json',
    traceArtifactPayload(),
  ));
  await setRangeValue(page, 1);
  await page.getByRole('button', { name: 'Agent' }).click();
  await page.getByText('Agent decision', { exact: true }).waitFor();
}

export async function loadFullPressDemo(page) {
  await page.getByLabel('Load replay').setInputFiles(join(ROOT, 'src', 'data', 'fullPressDemo', 'replay.json'));
  await page.getByLabel('Load press').setInputFiles(join(ROOT, 'src', 'data', 'fullPressDemo', 'press_traces.json'));
  await setRangeValue(page, 28);
}

export async function showConversation(page) {
  await page.getByRole('button', { name: 'Conversation' }).click();
  await page.getByText(/press messages/i).first().waitFor();
  await page.getByText('whispered to').first().waitFor();
}

export async function showForensic(page) {
  await page.getByRole('button', { name: 'Forensic' }).click();
  await page.getByText('Event JSON').waitFor();
}

export async function showSampleBatch(page) {
  await page.getByRole('button', { name: 'Sample batch' }).click();
  await page.getByRole('heading', { name: /runs, 4 players, seeds 101/i }).waitFor();
}

export async function showLiveView(page, liveBaseUrl) {
  await page.getByRole('tab', { name: 'Live' }).click();
  await page.getByLabel('Live API URL').fill(liveBaseUrl);
  await page.getByRole('region', { name: 'Live workbench' }).waitFor();
  await page.getByLabel('Nuclear War table').waitFor();
  await page.getByRole('heading', { name: 'Pending decision' }).waitFor();
  await page.getByLabel('Legal actions').waitFor();
}

export async function readScreenshotBytes(file) {
  return readFile(outputPath(file));
}

function filePayload(name, payload) {
  return {
    name,
    mimeType: 'application/json',
    buffer: Buffer.from(JSON.stringify(payload)),
  };
}
