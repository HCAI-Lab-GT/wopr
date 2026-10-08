import { formatPlayerId } from './replayFormatters.js';

const PREVIEW_LIMIT = 240;

export function summarizeDecisionTrace(trace, relatedAction) {
  if (!trace) return null;
  return {
    selectedActionId: trace.selected_action_id,
    selectedActionLabel: selectedActionLabel(trace, relatedAction),
    decisionType: trace.decision_type,
    validationStatus: validationStatus(trace),
    retryCount: trace.retries,
    validationErrors: trace.validation_errors ?? [],
    legalOptionGroups: legalOptionGroups(trace.legal_options ?? []),
    promptPreview: preview(trace.prompt ?? trace.prompts?.[0] ?? ''),
    responsePreview: preview(trace.raw_response ?? trace.raw_responses?.[0] ?? ''),
    parseResult: trace.parse_result,
    statedRationale: trace.stated_rationale,
    provider: providerSummary(trace),
    runtimeLabels: runtimeLabels(trace),
  };
}

function selectedActionLabel(trace, relatedAction) {
  const option = (trace.legal_options ?? []).find((item) => item.action_id === trace.selected_action_id);
  return option?.label ?? relatedAction?.action_type ?? trace.selected_action_id;
}

function validationStatus(trace) {
  const errors = trace.validation_errors ?? [];
  if (errors.length === 0) return 'Valid';
  if (trace.retries === 1) return 'Recovered after 1 retry';
  if (trace.retries > 1) return `Recovered after ${trace.retries} retries`;
  return 'Validation errors recorded';
}

function legalOptionGroups(options) {
  const groups = new Map();
  for (const option of options) {
    const family = familyLabel(option.action_id);
    groups.set(family, [...(groups.get(family) ?? []), {
      actionId: option.action_id,
      label: option.label ?? option.action_id,
    }]);
  }
  return [...groups.entries()].map(([family, groupOptions]) => ({ family, options: groupOptions }));
}

function familyLabel(actionId) {
  const [prefix] = String(actionId).split(':');
  if (!prefix) return 'Action';
  return titleCase(formatPlayerId(prefix));
}

function providerSummary(trace) {
  return {
    label: trace.provider_label,
    model: trace.provider_model,
    latencyMs: trace.provider_latency_ms,
    cost: trace.provider_cost,
    usage: trace.provider_usage,
  };
}

function runtimeLabels(trace) {
  return [trace.runtime_path, trace.runtime, trace.agent_runtime].filter(Boolean);
}

function preview(value) {
  const text = String(value ?? '');
  return text.length > PREVIEW_LIMIT ? `${text.slice(0, PREVIEW_LIMIT)}...` : text;
}

function titleCase(value) {
  return String(value)
    .split(' ')
    .filter(Boolean)
    .map((part) => `${part.charAt(0).toUpperCase()}${part.slice(1)}`)
    .join(' ');
}
