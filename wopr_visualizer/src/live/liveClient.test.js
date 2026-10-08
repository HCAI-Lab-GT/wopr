import { describe, expect, it } from 'vitest';
import { createLiveClient, LiveApiError } from './liveClient.js';

function jsonResponse(payload, options = {}) {
  return {
    ok: options.ok ?? true,
    status: options.status ?? 200,
    json: async () => payload,
  };
}

function nonJsonResponse(options = {}) {
  return {
    ok: options.ok ?? false,
    status: options.status ?? 500,
    json: async () => {
      throw new SyntaxError('Unexpected token < in JSON');
    },
  };
}

function recordingFetch(payload = { ok: true }) {
  const calls = [];
  const fetchImpl = async (url, options = {}) => {
    calls.push({ url, options });
    return jsonResponse(payload);
  };
  fetchImpl.calls = calls;
  return fetchImpl;
}

describe('createLiveClient', () => {
  it('requests live API endpoints with expected methods and bodies', async () => {
    const fetchImpl = recordingFetch({ ok: true });
    const client = createLiveClient('http://127.0.0.1:8765/api', fetchImpl);

    await client.getSession();
    await client.getState();
    await client.getDecision();
    await client.submitDecision('player_0:place', 3);
    await client.stepAgent(4);
    await client.getArtifacts();

    expect(fetchImpl.calls.map((call) => [call.url, call.options.method])).toEqual([
      ['http://127.0.0.1:8765/api/session', 'GET'],
      ['http://127.0.0.1:8765/api/state', 'GET'],
      ['http://127.0.0.1:8765/api/decision', 'GET'],
      ['http://127.0.0.1:8765/api/decision', 'POST'],
      ['http://127.0.0.1:8765/api/step-agent', 'POST'],
      ['http://127.0.0.1:8765/api/artifacts', 'GET'],
    ]);
    expect(JSON.parse(fetchImpl.calls[3].options.body)).toEqual({
      state_version: 3,
      action_id: 'player_0:place',
    });
    expect(JSON.parse(fetchImpl.calls[4].options.body)).toEqual({ state_version: 4 });
    expect(fetchImpl.calls[3].options.headers).toEqual({ 'Content-Type': 'application/json' });
    expect(fetchImpl.calls[4].options.headers).toEqual({ 'Content-Type': 'application/json' });
  });

  it('normalizes trailing slashes in the base URL', async () => {
    const fetchImpl = recordingFetch({ pending: false });
    const client = createLiveClient('http://127.0.0.1:8765///', fetchImpl);

    await client.getDecision();

    expect(fetchImpl.calls[0].url).toBe('http://127.0.0.1:8765/decision');
  });

  it('throws LiveApiError for structured HTTP error payloads', async () => {
    const fetchImpl = async () =>
      jsonResponse(
        { ok: false, error: { code: 'stale_state', message: 'State version is stale.' } },
        { ok: false, status: 409 },
      );
    const client = createLiveClient('http://127.0.0.1:8765', fetchImpl);

    await expect(client.submitDecision('player_0:place', 1)).rejects.toMatchObject({
      name: 'LiveApiError',
      code: 'stale_state',
      message: 'State version is stale.',
      status: 409,
    });
  });

  it('throws fallback LiveApiError for non-JSON HTTP error payloads', async () => {
    const fetchImpl = async () => nonJsonResponse({ status: 500 });
    const client = createLiveClient('http://127.0.0.1:8765', fetchImpl);

    await expect(client.getState()).rejects.toMatchObject({
      name: 'LiveApiError',
      code: 'api_error',
      message: 'API request failed.',
      status: 500,
    });
  });

  it('throws LiveApiError for ok false success payloads', async () => {
    const fetchImpl = async () =>
      jsonResponse({ ok: false, error: { code: 'invalid_body', message: 'Invalid request body.' } });
    const client = createLiveClient('http://127.0.0.1:8765', fetchImpl);
    const result = client.stepAgent(1);

    await expect(result).rejects.toBeInstanceOf(LiveApiError);
    await expect(result).rejects.toMatchObject({
      code: 'invalid_body',
      message: 'Invalid request body.',
      status: 200,
    });
  });
});
