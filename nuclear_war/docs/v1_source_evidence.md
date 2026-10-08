# Nuclear War V1 Source Evidence

This page records the source-evidence requirements that support
`docs/v1_acceptance.md`.

## Imported Bundle

- Raw research imports are preserved under `research/imports/`.
- The current imported bundle preserves the non-directory files listed in its
  `BUNDLE_FILE_MANIFEST.md`, and its source archive checksum is recorded.
- The full project import was compared against a fresh archive extraction with
  `diff -qr`.
- Downloaded rulebook PDFs and their extracted text are not redistributed in
  this repository. Source URLs are in the bundle's `source_index.csv`.
- The bundle's PDF verification report preserves page counts and SHA256 hashes.
- `source_index.csv` and `source_index.json` are the 34-ID source ledger for
  new rule and card provenance.

## Source Boundaries

- Variant metadata must not collapse imported schema boundaries: randomizer,
  population model, hand target, initial face-down cards, anti-missile turn
  jump, expansion sets, special powers, trading, press, and simultaneous orders.
- Exact card text is not a v1 acceptance requirement unless it comes from a
  physical copy or publisher authorized source.
- Public-safe card-effect evidence, once available, lives in
  `research/source_evidence/card_effect_evidence.jsonl`. The manifest records
  card identity, effect summary, evidence kind, private source reference, and
  second-pass status. It deliberately excludes exact card text.
- Public-safe expansion deck-composition evidence, once available, lives in
  `research/source_evidence/expansion_deck_composition.jsonl`. The manifest
  records registry identity, expansion set, count evidence, evidence kind,
  private source reference, and second-pass status. It deliberately excludes
  exact card text.
- Edition conflicts must be represented as variant choices or documented gaps,
  not silently merged into the default rules.

## Intake Gate

`nuclear-war validate-rules` reports `card_effect_evidence_manifest` and
`expansion_composition_evidence_manifest`. Missing manifests are the current
expected state and do not fail validation. Present manifests fail validation if
they are malformed, miss required public-safe fields, contain duplicate card or
registry IDs, reference unknown expansion registry IDs, mark second-pass
verification inconsistently, or contain restricted exact-text fields.
Live manifest records must be second-pass verified. If present live records are
still draft or otherwise unverified, `validate-rules` reports
`card_effect_evidence_promotion_errors` or
`expansion_composition_evidence_promotion_errors`.

Draft work should use `nuclear-war validate-source-evidence` with explicit
manifest paths before any records are copied into live manifest names. The
draft preflight reports `card_effect_evidence_coverage` and
`expansion_composition_evidence_coverage` so source workers can track missing,
recorded, verified, and unverified target IDs. Coverage is only a progress
report; it is not source evidence.
It also reports `card_effect_evidence_target_details` and
`expansion_composition_evidence_target_details` so those queues include
public-safe target metadata. Those details are capture aids only.
Current public-safe target metadata can be exported with
`nuclear-war source-evidence-targets`; that output is a capture aid only and is
not source evidence.
Draft JSONL stubs can be exported with
`nuclear-war source-evidence-draft-stubs`; those stubs are also capture aids
only and must be edited from real source work before promotion.
Official public source leads are listed in
`research/source_evidence/PUBLIC_SOURCE_LEADS.md`; that inventory is also only
a capture aid and does not supply source evidence.

These gates do not clear `card_effect_transcription`, expansion composition, or
edition blockers by themselves. Those blockers remain until the required source
evidence exists and the registry is updated in a separate rules-change branch.
