# Source Evidence Capture Runbook

This runbook is for physical-copy or publisher-authorized source work. It does not create source
evidence by itself, and it must not be used to change registry effects or expansion counts without
validated manifest records and a later rules-change branch.

## Scope

- Use this with `README.md`, `card_effect_evidence.template.jsonl`, and
  `expansion_deck_composition.template.jsonl`.
- Use `CAPTURE_CHECKLIST.md` for the current public-safe card IDs and expansion registry IDs that
  need source-evidence coverage.
- Use the imported gap checklist at
  `research/imports/2026-06-14_nuclear_war_card_game_research_bundle/07_gaps_and_next_steps/exact_text_gap_list.md`
  as the capture target list.
- Use `PUBLIC_SOURCE_LEADS.md` for current official public product and download leads.
- Capture only derived, public-safe evidence records in this repository.
- Keep photos, scans, and exact text outside the public repository.
- Use `nuclear-war source-evidence-targets` when a machine-readable public-safe target list is
  needed.

## Before Capture

- Confirm the copy or source is physical-copy evidence or publisher-authorized evidence.
- If publisher authorization is needed, send a request before drafting records from publisher
  materials.
- Check `PUBLIC_SOURCE_LEADS.md` before capture to distinguish public hosted leads from material
  that still needs physical-copy evidence or publisher authorization.
- Pick a private storage location outside the public repository for photos, scans, and notes.
- Export current public-safe targets with `uv run nuclear-war source-evidence-targets` if the
  capture session needs JSON target metadata.
- Export draft JSONL stubs with `uv run nuclear-war source-evidence-draft-stubs --kind card-effects`
  or `--kind expansion-composition` when a capture session needs starter records.
- Use generic private references in draft records, such as
  `private/source-capture/card-front-001.jpg`.
- Do not create `card_effect_evidence.jsonl` or `expansion_deck_composition.jsonl` before the
  first-pass draft records are reviewed.

## Capture Session

- Photograph each unique card front and back.
- Photograph rules sheets, spinner, mats, population cards, and deck or back identifiers.
- Count duplicates by card name and deck or back identifier.
- Record edition, deck identifier, derived effect summary, count, and ambiguous fields in private
  working notes.
- Do not copy exact card text, official text, unofficial text, or art into public files.

## Draft Records

- Start from the matching `.template.jsonl` file.
- Or generate current target-aligned draft stubs with `source-evidence-draft-stubs`.
- Keep `evidence_kind` as `physical_copy` for private captures or `publisher_authorized_source`
  for authorized source records.
- Replace generated TODO fields and generic `private/` references from actual source work before
  promotion.
- For physical-copy records, keep source references under `private/`.
- Use `verification_status: "draft"` and `verified_by_second_pass: false` during first pass.
- Check drafts before promotion:

```bash
uv run nuclear-war validate-source-evidence \
  --card-effects /path/to/card_effect_evidence.draft.jsonl \
  --expansion-composition /path/to/expansion_deck_composition.draft.jsonl
```

- Read the coverage payloads after preflight.
- Use `missing_ids` as the remaining capture target list.
- Use `unverified_ids` as the second-pass review queue.
- Use the target-detail payloads for public-safe names, types, counts, and expansion metadata in
  those queues.
- Do not treat coverage as source evidence or as a reason to clear blockers.

## Second Pass

- Have a second pass verify card identity, counts, edition boundary, and derived effect summary.
- For card-effect records, confirm each `card_id` matches the active registry.
- For expansion composition records, confirm each `registry_id` matches the expansion catalog.
- Change `verification_status` to `second_pass_verified` only after review.
- Set `verified_by_second_pass` to `true` only after review.

## Promotion Boundary

- Copy reviewed card-effect records into `card_effect_evidence.jsonl` only after the draft preflight
  passes.
- Copy reviewed expansion records into `expansion_deck_composition.jsonl` only after the draft
  preflight passes.
- Live manifest validation fails for records that are not second-pass verified.
- Run `uv run nuclear-war validate-rules` after adding live manifest records.
- Make effect metadata or expansion count changes in a separate registry-change branch after live
  manifests validate.

## What Not To Do

- Do not add source photos, scans, exact text, art, or private working notes to the repository.
- Do not promote draft records that have not passed second-pass review.
- Do not treat templates as source evidence.
- Do not clear source blockers just because draft records exist.
- Do not enable alternate editions, expansion counts, or registry effect changes in this branch.
