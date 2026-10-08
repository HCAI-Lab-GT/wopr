# Source Research Policy

This page records how I use imported Nuclear War research materials.

## Current Import

The current raw import is:

`research/imports/2026-06-14_nuclear_war_card_game_research_bundle/`

It includes public-source summaries, card inventories, variant notes, source
notes, and next-step checklists.

The imported folder holds the files listed in `BUNDLE_FILE_MANIFEST.md`, taken
from `nuclear_war_card_game_research_bundle.zip`. I use the imported folder as
the project copy. I do not use the zip file as a runtime dependency.

The archive passed `unzip -t` on 2026-06-14 and has SHA256
`2d3e23e2bd9322519c52cef7482e3dbab271de35b1e5801a9963311ebc04ee0d`.
An extracted archive tree matched the project import under `diff -qr` on
2026-06-14.
The imported `source_index.json` contains 34 source IDs.

The bundle includes a PDF verification report with page counts and SHA256
hashes for the downloaded PDFs. Those hashes are provenance evidence for the
import, not proof that a PDF mirror is authoritative for all editions.
The downloaded rulebook PDFs and their extracted text are not redistributed in
this repository, so the public copy is a subset of the archive. Source URLs are
in the bundle's `source_index.csv`.

## Source Priority

I rank sources in this order for implementation decisions:

1. Publisher-hosted current rules and support PDFs.
2. Downloaded classic rules PDF mirrors.
3. Older spinner-era scans.
4. Community card lists and FAQs for names, counts, and edge-case leads.
5. Postal-play rules for PBM and press/no-press structure.
6. Historical and cultural sources for context only.
7. Community implementations for comparison only.

The bundle's source index gives stable source IDs. V1 implementation notes
should prefer those IDs over older local labels:

- `OFF-001` through `OFF-004` for current publisher Nuclear Destruction
  materials.
- `MIR-001` for the later base rules mirror with two ten-sided dice.
- `MIR-002` for the older spinner-era scan.
- `UNOFF-001` for the postal/PBM rules.
- `COMM-*` for community card inventory and FAQ leads.

Older registry labels such as `publisher_cardlist`, `combined_rules`, and
`rulesheet_pdf` are legacy labels. `nuclear-war validate-rules` loads source
IDs from the imported `source_index.json` and reports
`unresolved_source_labels` so active registry records cannot keep those labels
without failing the v1 rule-validation gate.

## V1 Source Boundary

V1 remains a deterministic classic/base and postal no-press implementation.
The imported bundle supports this by clarifying edition boundaries:

- Classic spinner-era sources and later two-d10 sources may disagree.
- Population deck size may be 20 or 40 cards depending edition.
- Hand targets differ by source.
- Current Nuclear Destruction rules are a related modern branch, not the active
  v1 rule source unless a future edition module selects them.
- Expansion mechanics should remain configurable pending exact card metadata.
- Imported expansion inventory CSVs are source leads only. Expansion
  `count_in_deck` values require a physical-copy or publisher-authorized
  composition record before registry counts can change.
- No official no-press source variant was established by the bundle. V1
  no-press is a controlled WOPR mode that disables communication while retaining
  non-communication postal mechanics from `UNOFF-001`.

## Active V1 Variant

The active v1 variant is `base_later_two_d10`.

Runtime validation reports this as:

- hand draw target: 10;
- population deck size model: 40 cards;
- randomizer: `base_two_d10_fallout_chart`;
- initial face-down cards: 2;
- anti-missile turn jump: true;
- expansion sets: none;
- special powers enabled: false;
- trading enabled: false;
- press enabled: false;
- simultaneous orders: false.

This active runtime combines the later two-d10 fallout chart with the 40-card
population deck model already implemented in the engine. That source boundary
is intentional for the current deterministic v1 substrate and remains recorded
as an edition-sensitive field before any future variant module can select a
different population model.

Classic spinner, current Nuclear Destruction, postal press, and combined
expansion models remain future variant inputs unless explicitly selected later.

The imported simulation schema also names variant fields that affect edition
boundaries: `initial_face_down_cards`, `anti_missile_turn_jump`,
`expansion_sets`, `special_powers_enabled`, and `trading_enabled`. The active
runtime payload now reports fixed v1 values for those fields before any future
edition module can choose different values.

## Exact Text Boundary

I do not treat the imported card inventories as exact card text. For v1, card
records should use effect summaries, source IDs, and confidence fields. Exact
front text, card art, and disputed edition behavior should remain out of public
simulation data unless verified from a physical copy or authorized source.

The physical-copy capture checklist in
`07_gaps_and_next_steps/exact_text_gap_list.md` is the next source of truth for
exact-card transcription. Until that work happens, the default registry should
continue to avoid `exact_text`, `exact_front_text`, and other restricted text
fields.

The import's card-data README lists transcription fields I should preserve when
physical-copy work starts: edition in hand, deck identifier, exact front text,
capacity or megatonnage, population delta, timing window, targeting rule,
defense interactions, private image filename, transcriber, and second-pass
verification.

The public-safe card-effect source-evidence intake manifest is
`research/source_evidence/card_effect_evidence.jsonl`. It records derived effect
evidence and private source references only. It must not include exact card
text, official text, unofficial text, or other rights-restricted wording.

The public-safe expansion deck-composition intake manifest is
`research/source_evidence/expansion_deck_composition.jsonl`. It records
registry identity, expansion set, count evidence, evidence kind, private source
reference, and second-pass status only. It must not include exact card text,
official text, unofficial text, or other rights-restricted wording.

`nuclear-war validate-rules` reports both manifests as `missing` until
physical-copy or publisher-authorized evidence exists. Missing manifests do not
fail validation; present but malformed, unverified, duplicate, unknown-registry,
or exact-text-bearing manifests do fail validation.

The capture workflow and draft record shapes live in
`research/source_evidence/README.md`. The `.template.jsonl` files in that
directory are not source evidence and are not read by `validate-rules`.
Draft records should be checked with `nuclear-war validate-source-evidence`
before promotion. That command reports `card_effect_evidence_coverage` and
`expansion_composition_evidence_coverage` as capture-progress payloads only.
It also reports `card_effect_evidence_target_details` and
`expansion_composition_evidence_target_details` as public-safe capture aids for
missing and unverified queues.
`nuclear-war source-evidence-targets` exports the current public-safe target
metadata for capture sessions, but that output is not source evidence.
`nuclear-war source-evidence-draft-stubs` exports draft JSONL starter records
from the same target metadata, but those records are capture aids only and must
be edited from actual source work before promotion.
Private publisher correspondence and exact source text must stay out of the
public repository.
Official public source leads are listed in
`research/source_evidence/PUBLIC_SOURCE_LEADS.md`; that inventory is a capture
aid only and does not create source evidence.
Live records must be second-pass verified; otherwise `validate-rules` reports
`card_effect_evidence_promotion_errors` or
`expansion_composition_evidence_promotion_errors`.

`nuclear-war validate-rules` reports `restricted_text_fields` so exact or
unofficial text fields do not enter the active registry by accident.

## Implementation Rule

When a source conflict affects behavior, I should either:

- implement it behind an explicit variant flag, or
- document the gap in `docs/rule_fidelity_matrix.md`.

I should not silently collapse multiple editions into one rule.
