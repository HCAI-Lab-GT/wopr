import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { createServer } from 'node:net';

const START_TIMEOUT_MS = 30000;

export const delay = (ms) => new Promise((resolve) => { setTimeout(resolve, ms); });

export function startProcess(command, args, options) {
  const child = spawn(command, args, { ...options, stdio: ['ignore', 'pipe', 'pipe'] });
  child.output = '';
  for (const stream of [child.stdout, child.stderr]) {
    stream.setEncoding('utf8');
    stream.on('data', (chunk) => { child.output += chunk; });
  }
  return child;
}

export async function stopProcess(child) {
  if (child.exitCode !== null || child.signalCode !== null) return;
  const closed = once(child, 'close');
  child.kill('SIGTERM');
  const timedOut = await Promise.race([
    closed.then(() => false),
    delay(5000).then(() => true),
  ]);
  if (timedOut && child.exitCode === null && child.signalCode === null) {
    child.kill('SIGKILL');
    await once(child, 'close');
  }
}

export async function waitForEndpoint(url, child, label, json = false) {
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

export function findUnusedPort(host) {
  return new Promise((resolve, reject) => {
    const server = createServer();
    server.unref();
    server.on('error', reject);
    server.listen(0, host, () => {
      const address = server.address();
      const port = typeof address === 'object' && address !== null ? address.port : null;
      server.close(() => (port === null ? reject(new Error('No local port assigned.')) : resolve(port)));
    });
  });
}
