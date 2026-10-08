# Nuclear War Research Imports

This folder stores source bundles and derived notes that support the
deterministic Nuclear War implementation.

## Contents

- `imports/2026-06-14_nuclear_war_card_game_research_bundle/`: the imported
  research bundle.
- `source_evidence/`: public-safe capture instructions, a public source-lead
  inventory, and draft manifest templates for card-effect and expansion
  deck-composition evidence.
- `llm_model_calibration/data/serverless_catalog_2026-07-05.json`: a snapshot
  of a provider's serverless model catalog and listed prices. The
  `llm-model-scorecard` example config
  `docs/examples/llm_model_scorecard_catalog_demo.json` reads it.

## 2026-06-14 Bundle Use

I treat this bundle as research evidence, not as direct executable rules data.
It contains source notes, card inventories, variant notes, and
simulation-model sketches.

The imported project copy holds the files listed in the bundle manifest
(`BUNDLE_FILE_MANIFEST.md`), taken from
`nuclear_war_card_game_research_bundle.zip`.
The source archive passed `unzip -t` on 2026-06-14 and has SHA256
`2d3e23e2bd9322519c52cef7482e3dbab271de35b1e5801a9963311ebc04ee0d`.
An extracted archive tree matched the full imported project copy under
`diff -qr` on 2026-06-14.
The imported `source_index.json` contains 34 source IDs.

Downloaded rulebook PDFs and their extracted text are not redistributed in this
repository, and neither are the bundle's original AI prompt notes. Source URLs
are in the bundle's `source_index.csv`.

The useful v1 inputs are:

- `source_index.csv` and `source_index.json` for source lookup.
- `docs/source_research_policy.md` for source priority ordering.
- `02_rules_and_variants/rules_reconstruction_summary.md` for edition-sensitive
  rule conflicts.
- `03_card_data/base_game_card_inventory.csv` for first-pass card names and
  counts.
- `04_simulation_model/rules_variants.json` for variant boundaries.
- `07_gaps_and_next_steps/exact_text_gap_list.md` for remaining transcription
  work.
- `BUNDLE_FILE_MANIFEST.md` and `99_sources/pdf_verification_report.md` for
  import audit details.
- `source_evidence/README.md` for public-safe capture instructions and draft
  manifest templates.

I do not use the bundle to publish exact card text. Exact card wording and
edition-specific card behavior still require a physical copy or publisher
authorized source.

The runtime `active_variant` payload records the imported schema fields with
fixed v1 values. Future edition modules need explicit variant choices instead
of reusing those defaults silently.

## Registry Source Labels

The active runtime registry uses imported source-index IDs in its `sources`
fields. Rule validation loads IDs from `source_index.json` and reports
`unresolved_source_labels` so legacy or unmapped labels are visible before v1
experiment work relies on them.
