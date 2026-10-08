# Live LM Pilot Experiment Runbook

This runbook covers running live language-model games. It covers the two
checked-in pilot configs, the preflight command, where artifacts land, how to
validate and inspect them, the failure modes the harness already handles, and
a measured cost estimate.

The skipped tests in a default suite run are live checks. Two of them cover
these pilots, and they prove different things:
`tests/integration/test_llm_http_live_smoke.py` proves one real completion
call through the pilot-1 client path against whatever endpoint
`WOPR_LLM_BASE_URL` names; `tests/integration/test_concordia_http_live_smoke.py`
proves one real Concordia game turn, but only against Together's hard-coded
endpoint via the demo config, not pilot 2's press-light config (see the
gating note in section 2).
Everything else in this kit is proven offline by
`tests/integration/test_pilot_example_configs.py` and
`tests/unit/test_llm_preflight.py`. A four-seat no-press demo run with
`llm_http` seats is checked in under `docs/demo_runs/2026-06-22-4llm-no-press/`.

## 1. The two pilots

| Pilot | Config | Shape |
| --- | --- | --- |
| No-press baseline comparison | `docs/examples/pilot_no_press_llm_http.json` | 4 players, `runs: 10`, seeds 101–110, `max_turns: 40`. One `llm_http` seat (`player_0`) vs `random`, `heuristic`, `decision_heuristic`. |
| Press-light Concordia | `docs/examples/pilot_press_light_concordia.json` | 4 `concordia_http` seats, seed 211, `max_turns: 40`, `press: {"mode": "press_light", "enabled": true}`. One game per invocation. |

Both configs are endpoint-agnostic and contain **no secrets**: every client
field is env-var driven (`base_url_env`, `model_env`, `api_key_env`).

## 2. Environment variables

All three variables drive both pilot configs:

```bash
export WOPR_LLM_BASE_URL="https://api.together.xyz/v1"   # any OpenAI-compatible /v1 base
export WOPR_LLM_MODEL="meta-llama/Llama-3.3-70B-Instruct-Turbo"
export TOGETHER_API_KEY="..."                             # bearer token; the env-var NAME is fixed, the provider is not
```

`TOGETHER_API_KEY` is just the variable name the pilot configs reference —
point `WOPR_LLM_BASE_URL` at vLLM/SGLang/OpenAI/etc. and put that provider's
key in `TOGETHER_API_KEY`. For a keyless local endpoint you would need a
config variant without `api_key_env` (not checked in).

The two live smoke tests are gated differently:

- `tests/integration/test_llm_http_live_smoke.py` skips unless all three
  variables are set, and hits whatever endpoint `WOPR_LLM_BASE_URL` names —
  safe with any provider.
- `tests/integration/test_concordia_http_live_smoke.py` skips only on
  `TOGETHER_API_KEY` and `WOPR_LLM_MODEL`. It ignores `WOPR_LLM_BASE_URL` and
  always POSTs to the hard-coded `https://api.together.ai/v1` in
  `docs/examples/concordia_no_press_together_demo.json` (seed 83, no press,
  `max_turns` forced to 1 — the demo config, not pilot 2's press-light
  config). **Only run it when `TOGETHER_API_KEY` actually holds a Together
  key**: against any other provider it would send that provider's key as a
  Bearer header to Together.

All commands below run from `nuclear_war/` via `uv`.

## 3. Preflight (one cheap completion call)

```bash
uv run nuclear-war llm-preflight --config docs/examples/pilot_no_press_llm_http.json
```

Loads the config, resolves the first HTTP seat's client (including env vars),
and makes ONE completion call capped at 32 output tokens, temperature 0. On
success it prints a JSON report:

```json
{
  "api_key_env": "TOGETHER_API_KEY",
  "config_kind": "no_press_llm_http",
  "endpoint": "https://api.together.xyz/v1/chat/completions",
  "latency_ms": 412,
  "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
  "ok": true,
  "provider_label": "together",
  "response_snippet_chars": 29,
  "seat": "player_0",
  "transport_retries": 0
}
```

The API key is never printed — only the env-var name. Missing env vars or a
failing endpoint exit with code 2 and a one-line error on stderr. Run it
against both pilot configs (it understands the Concordia shape too), then run
the live smokes (gating differences in section 2 — drop the Concordia smoke
from the command unless your key is a Together key):

```bash
uv run nuclear-war llm-preflight --config docs/examples/pilot_press_light_concordia.json
uv run --extra dev python -m pytest -o addopts="" -q \
  tests/integration/test_llm_http_live_smoke.py \
  tests/integration/test_concordia_http_live_smoke.py
```

## 4. Run pilot 1 — no-press batch

```bash
uv run nuclear-war llm-experiment \
  --config docs/examples/pilot_no_press_llm_http.json \
  --out-dir runs/pilot_no_press
```

Artifacts land in `runs/pilot_no_press/`:

- `seed-101.replay.json` … `seed-110.replay.json` — engine replays.
- `seed-101.replay.traces.json` … — decision-trace sidecars (prompts, raw
  responses, parse results, retries, provider usage/latency).
- `summary.json` — aggregate outcomes, per-agent decision metrics, config
  snapshot.
- Games stream to disk as they finish; a mid-batch crash leaves the completed
  games plus `failure_marker.json` (requested/completed runs, failed seed,
  error) instead of discarding everything.

Validate the finished batch (checks the config snapshot, seed sequence,
variant, player count, outcomes, and every linked replay/trace artifact):

```bash
uv run nuclear-war llm-summarize runs/pilot_no_press/summary.json
```

## 5. Run pilot 2 — press-light Concordia game

```bash
uv run nuclear-war concordia-demo \
  --config docs/examples/pilot_press_light_concordia.json \
  --out-dir runs/pilot_press_light
```

Artifacts:

- `wopr/replay.json`, `wopr/traces.json` — replay + decision-trace sidecar.
- `concordia/run_summary.json` — winner, turns, trace/retry/fallback counts,
  `press_message_count`, per-player decision metrics.
- `concordia/config_snapshot.json`, `concordia/agent_metadata.json`,
  `concordia/runtime_status.json`.
- `concordia/press_traces.json` — the press artifact (one public message per
  living player per round in press-light mode).
- On a run failure the command writes `concordia/failure_snapshot.json` and
  exits nonzero.

Repeat with different `seed` values (edit a copy of the config) for more
games; the command runs one game per invocation.

## 6. Inspecting decisions in the replay workbench

The workbench lives in the sibling `wopr_visualizer/` package (Vite app —
`npm install && npm run dev` there).

- Pilot 1: **Load batch directory** and select `runs/pilot_no_press/` — every
  `seed-*.replay.json`, `seed-*.replay.traces.json`, and `summary.json` is
  indexed. The Batch view shows aggregate tiles (invalid actions, retries,
  provider latency/cost totals); click a run to drop into the replay view.
- Pilot 2: **Load replay** with `wopr/replay.json`, then **Load traces** with
  `wopr/traces.json`, then **Load press** with `concordia/press_traces.json`.
- The **Decision** inspector tab shows, per decision: the rendered
  observation, legal options, the exact prompt(s), raw response(s), parse
  result, retries, validation errors, the selected action, and provider
  metadata (label, model, latency, usage) when present.

## 7. Failure modes already handled, and the metrics that reveal them

| Failure mode | Handling | Where it shows up |
| --- | --- | --- |
| Transient HTTP 429/5xx | Transport retries the same call up to 3 attempts inside one completion (`llm_http_client.py`) | `transport_retries` in preflight; `provider_transport_retries` on traces |
| Timeout / connection drop / non-retryable HTTP error | Decision-level re-issue within the same `max_retries` budget (both pilots), tallied separately from output reprompts. If every attempt at one decision transport-fails: pilot 1 aborts the batch keeping completed games plus `failure_marker.json`; pilot 2 writes `concordia/failure_snapshot.json` and exits nonzero | `recoverable_provider_retries` on traces; `recoverable_provider_retry_count` in the Concordia summary |
| Model returns an illegal or unparseable action | Reprompt once with the validation error, then fallback policy: `first` (take the engine-ordered first legal action) or `pass` (decline-style option) | `invalid_action_count` / `invalid_action_rate`; `fallback_used` on traces, `fallback_count` in the Concordia summary |
| Crash mid-batch (pilot 1) | Per-game incremental artifact writes + `failure_marker.json` | completed `seed-*.replay.json` files remain on disk |
| Run failure (pilot 2) | `concordia/failure_snapshot.json` with config snapshot and failure context | load via the workbench's **Load failure** |
| Misconfiguration (missing env var / bad config) | Fail fast before any game: preflight and config parsers exit 2 with a message | stderr, exit code |

Watch `invalid_action_rate` and `retry_rate` first: a healthy live seat should
keep both near zero. A high `fallback_count` means the "LLM" results are
actually first-legal results — treat those games as harness successes but
model failures.

## 8. Cost estimate (measured, offline)

Method: play the offline variants of both pilots (HTTP seats swapped for
`llm_first_legal`/`concordia_first_legal`, exactly as the CI test does),
count decisions, and measure the actual prompt character sizes stored in the
trace artifacts. **Tokenization assumption: 1 token ≈ 4 characters** (typical
BPE ratio for English prose; check your provider's tokenizer for precision).

Measured on this checkout:

| Quantity | Pilot 1 (seed 101, 1 LLM seat) | Pilot 2 (seed 211, 4 LLM seats + press) |
| --- | --- | --- |
| Game length | 23 turns | 6 turns |
| LLM decision calls per game | 62 | 82 |
| Press calls per game | — | 18 |
| Prompt chars per game | 573,864 (mean 9,256; min 2,975; max 14,523) | 815,857 decision (mean 9,949) + 52,114 press (mean 2,895) |
| Input tokens per game (chars ÷ 4) | ≈ 143,500 | ≈ 217,000 |
| Output-token cap per call (`max_tokens`) | 256 | 512 |
| Output tokens per game (upper bound) | 62 × 256 = 15,872 | 100 × 512 = 51,200 |
| **Pilot total input** | 10 games ≈ **1.43 M tokens** | 1 game ≈ **0.22 M tokens** |
| **Pilot total output (upper bound)** | ≤ **0.16 M tokens** | ≤ **0.05 M tokens** |

Cost formula, with prices in USD per 1M tokens:

```
cost = input_millions × P_in + output_millions × P_out
pilot 1: 1.43 × P_in + 0.16 × P_out
pilot 2: 0.22 × P_in + 0.05 × P_out
```

| P_in / P_out ($ per 1M) | Pilot 1 (10 games) | Pilot 2 (1 game) |
| --- | --- | --- |
| 0.10 / 0.10 (cheap open-weights serving) | $0.16 | $0.03 |
| 0.88 / 0.88 (mid-tier hosted 70B class) | $1.40 | $0.24 |
| 3.00 / 15.00 (frontier API class) | $6.68 | $1.42 |

Caveats, in the honest direction (costs can only grow toward these bounds):

- The measured offline games ended at turns 23 and 6 of the 40-turn cap. A
  live model that plays differently can run longer; decision counts scale
  roughly linearly with turns, so budget up to ~2× (pilot 1) or ~6× (pilot 2,
  which also adds press calls every round) if games run to the cap.
- Each decision may be retried once (`max_retries: 1`), so worst case doubles
  the call count. Transport-level 429/5xx retries resend the same request up
  to 2 extra times on top of that.
- Output figures use the `max_tokens` cap; real completions are usually much
  shorter, so actual output spend will be lower.

## 9. Offline dry-run (no endpoint, no key)

The exact configs above are CI-guarded:

```bash
uv run --extra dev python -m pytest -o addopts="" -q \
  tests/integration/test_pilot_example_configs.py tests/unit/test_llm_preflight.py
```

This loads both pilot configs through their real parsers and plays one full
offline game each (`llm_http → llm_first_legal`,
`concordia_http → concordia_first_legal`) with validated artifacts, so the
checked-in configs cannot rot silently.
