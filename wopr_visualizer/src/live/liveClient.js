export class LiveApiError extends Error {
  constructor(code, message, status) {
    super(message);
    this.name = 'LiveApiError';
    this.code = code;
    if (status !== undefined) {
      this.status = status;
    }
  }
}

export function createLiveClient(baseUrl, fetchImpl = fetch) {
  const apiBaseUrl = normalizeBaseUrl(baseUrl);
  return {
    getSession: () => request(fetchImpl, apiBaseUrl, '/session'),
    getState: () => request(fetchImpl, apiBaseUrl, '/state'),
    getDecision: () => request(fetchImpl, apiBaseUrl, '/decision'),
    submitDecision: (actionId, stateVersion) =>
      request(fetchImpl, apiBaseUrl, '/decision', {
        method: 'POST',
        body: { state_version: stateVersion, action_id: actionId },
      }),
    stepAgent: (stateVersion) =>
      request(fetchImpl, apiBaseUrl, '/step-agent', {
        method: 'POST',
        body: { state_version: stateVersion },
      }),
    getArtifacts: () => request(fetchImpl, apiBaseUrl, '/artifacts'),
  };
}

function normalizeBaseUrl(baseUrl) {
  return String(baseUrl).replace(/\/+$/, '');
}

async function request(fetchImpl, baseUrl, path, options = {}) {
  const method = options.method ?? 'GET';
  const fetchOptions = { method };
  if (options.body !== undefined) {
    fetchOptions.headers = { 'Content-Type': 'application/json' };
    fetchOptions.body = JSON.stringify(options.body);
  }
  const response = await fetchImpl(`${baseUrl}${path}`, fetchOptions);
  if (!response.ok) {
    const payload = await parseErrorPayload(response);
    throw apiError(payload, response.status);
  }
  const payload = await response.json();
  if (payload?.ok === false) {
    throw apiError(payload, response.status);
  }
  return payload;
}

async function parseErrorPayload(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function apiError(payload, status) {
  const error = payload?.error;
  if (error && typeof error.code === 'string' && typeof error.message === 'string') {
    return new LiveApiError(error.code, error.message, status);
  }
  return new LiveApiError('api_error', 'API request failed.', status);
}
