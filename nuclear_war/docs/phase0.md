# Phase 0 Legacy Guardrails

I keep Phase 0 infrastructure as a compatibility layer while v1 work uses the
real rules engine.

- Central config in `src/nuclear_war_env` with immutable defaults
- Validation script `scripts/validate-phase` enforcing the 150-line limit and running lint, format, type checks, tests, and docs
- `benchmarks/run_benchmarks.py` writes Phase 0 setup plus table and postal
  no-press simulation timing to `benchmarks/results/latest.json` and compares
  it to `benchmarks/baselines/v1_guardrails.json`. The comparison uses absolute
  wall-clock times, so it depends on the machine and is not part of
  `scripts/validate-phase`.
- Documentation generation through `pdoc` writing to `build/docs`
- Real v1 PettingZoo factories are `create_aec_env`, `create_parallel_env`,
  `create_table_env`, and `create_postal_env`
- Legacy stub PettingZoo environments remain available through
  `create_phase0_aec_env` and `create_phase0_parallel_env`
- PettingZoo API compliance targets the real v1 table and postal environments.
  Legacy stubs are covered only as compatibility factories.
- `nuclear_war/.github/workflows/` holds `ci.yml` and `release.yml`, which run the
  guardrails. GitHub only runs workflows from the repository root, so they are
  not active; the root workflow runs pytest and ruff.

Usage checklist:

1. `uv pip install --system -e .[dev]`
2. `scripts/validate-phase` (the test suite includes PettingZoo compliance)
3. Optionally run `benchmarks/run_benchmarks.py` and review `benchmarks/results/latest.json` for timing data

I revisit this document whenever the guardrails evolve.
