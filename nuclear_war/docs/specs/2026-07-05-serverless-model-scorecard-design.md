# Serverless Model Scorecard Design

Date: 2026-07-05

## Goal

Build a scorecard for every serverless chat model listed in the current
provider catalog so I can choose models for WOPR LLM and Concordia experiments
with observed evidence, not only price and context metadata.

The scorecard has three stages:

1. Catalog fit for all chat models.
2. Low-cost working-model calibration for all chat models with bounded calls.
3. Role-play and experiment-quality calibration for operationally viable models.

## Scope

In scope: all 23 serverless chat model IDs from the current catalog snapshot, a
predicted score from documented metadata, a minimal empirical gate for every
listed chat model including expensive models, trace-backed operational scores,
and later role-play scoring for experiment suitability.

Out of scope: image, video, audio, embedding, rerank, moderation, dedicated
endpoint models, fine-tuning, human play, and long overnight batches before
bounded calibration artifacts validate.

## Stage 1: Catalog Fit

Stage 1 uses only catalog data and official recommendations. It does not claim
observed model quality.

Each model gets `input_price_per_1m`, `cached_input_price_per_1m`,
`output_price_per_1m`, `context_length`, `structured_outputs`,
`function_calling`, `quantization`, `recommended_use_cases`, and
`catalog_risk_flags`.

The predicted fit score weights cost fit, context fit, structured-output
support, function-calling support, official recommendation category, and known
WOPR prompt risks.

Catalog-only ratings must be labeled `predicted`, not `measured`.

## Stage 2: Low-Cost Working-Model Calibration

Stage 2 runs every serverless chat model through the same minimal empirical
gate. This includes expensive models, but the run depth is capped.

Minimal gate per model:

1. Direct JSON response smoke.
2. One WOPR-native no-press one-turn run with one provider-backed seat.
3. Trace artifact validation.

Measured fields: direct smoke result, WOPR one-turn result, parse validity,
invalid action count, retry count, fallback count, provider latency, prompt
tokens, completion tokens, total tokens, estimated cost, output cap needed for
final JSON, and provider error class when failure occurs.

Stage 2 optimizes for a low-cost working model. A model can pass even if its
role-play quality is unknown. A model fails this stage if it cannot reliably
produce a legal action under bounded settings.

To control spend, each model starts with one seed and `max_retries=0`. If the
failure is empty final content with a length finish reason, the runner may try
one larger output cap. If the second attempt fails, the model is marked
`stage2_failed_cap_or_content`.

## Stage 3: Role-Play And Experiment Quality

Stage 3 runs only after Stage 2 identifies operationally viable models. It
scores qualities that require traces and human-readable responses.

Measured dimensions: character consistency, role-specific voice, strategic
coherence, rationale-action alignment, legal-option grounding, consistency
across seeds, tendency to invent unavailable actions, response verbosity,
press-mode usefulness, and Concordia native suitability.

Stage 3 should include both no-press and press-ladder prompts. The output is not
only pass/fail. It should preserve representative trace snippets so ratings can
be audited later.

## Scorecard Outputs

The scorecard should write `catalog_scorecard.json`,
`stage2_calibration_results.json`, `stage3_roleplay_results.json`, and
`scorecard_summary.md`.

The summary separates predicted catalog fit, measured operational fit, measured
role-play and experiment fit, cost estimate, and recommended use.

Recommended-use labels are `primary_low_cost`, `backup_low_cost`,
`roleplay_candidate`, `concordia_candidate`, `comparison_anchor`, and
`avoid_for_now`.

## Safety And Cost Controls

Calibration must be sequential by default because rate limits are dynamic per
model. The runner should support a maximum model count, maximum attempts per
model, and maximum estimated spend. It should stop on repeated provider errors
instead of retrying indefinitely.

Secrets must stay in environment variables. API keys, raw headers, and provider
account details must not be written to artifacts.

## Acceptance Criteria

- All 23 chat models appear in the catalog scorecard.
- All 23 chat models receive at least the minimal Stage 2 empirical gate, unless
  a provider error prevents access.
- Every measured score links to trace-backed evidence or a recorded failure.
- Stage 2 results identify at least one low-cost working model or explain why no
  candidate passed.
- Stage 3 is clearly gated behind Stage 2 survival.
- Documentation distinguishes predicted and measured scores.
