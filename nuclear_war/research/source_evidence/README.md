# Source Evidence Capture Packet

This directory is the staging area for source evidence that feeds rules and card verification.
The template files are not evidence. They show the public-safe JSONL shape that future source work
must fill from a physical copy or publisher-authorized source.

## Live Manifest Paths

`nuclear-war validate-rules` reads only these live manifest names:

- `card_effect_evidence.jsonl`
- `expansion_deck_composition.jsonl`

Missing live manifests are non-failing. Do not create either live manifest until source material
has been captured and checked.
When live manifest files are present, live manifest validation requires second-pass verified
records. Draft records can pass explicit draft preflight, but they fail under `validate-rules`
when copied into `card_effect_evidence.jsonl` or `expansion_deck_composition.jsonl`.

## Templates

- `card_effect_evidence.template.jsonl`
- `expansion_deck_composition.template.jsonl`

Each template is a draft record that passes the public-safe validators. Copy a template record into
the matching live manifest only after replacing every source reference with a real private capture
reference and completing the review fields.
For card-effect evidence, `card_id` must match an existing active registry id.

Use `CAPTURE_RUNBOOK.md` for the physical-copy or publisher-authorized source capture workflow.
Use `CAPTURE_CHECKLIST.md` for the current public-safe target ID list.
Use `PUBLIC_SOURCE_LEADS.md` for current official public download leads from the imported source
index.

Draft files can be checked before they become live manifests:

```bash
uv run nuclear-war validate-source-evidence \
  --card-effects /path/to/card_effect_evidence.draft.jsonl \
  --expansion-composition /path/to/expansion_deck_composition.draft.jsonl
```

The preflight command reads only the paths passed on the command line. It does not create or read
the live manifest files unless those live paths are passed explicitly.

Current public-safe capture target metadata can be exported without evidence files:

```bash
uv run nuclear-war source-evidence-targets
```

The target export lists card and expansion IDs, public names, types, counts, and supported modes.
It is a capture aid only. It does not read private files, create manifests, or clear blockers.

The command also reports `card_effect_evidence_coverage` and
`expansion_composition_evidence_coverage` for the supplied paths. Coverage is a capture-progress
report, not source evidence. It lists `required_ids`, `recorded_ids`, `verified_ids`,
`missing_ids`, and `unverified_ids` so source workers can see what still needs draft capture or
second-pass review. Incomplete coverage does not fail validation by itself.
Draft preflight also reports `card_effect_evidence_target_details` and
`expansion_composition_evidence_target_details` with public-safe metadata for the missing and
unverified queues. These details are capture aids only; they are not evidence records.

Draft JSONL stubs can be exported from current target metadata:

```bash
uv run nuclear-war source-evidence-draft-stubs --kind card-effects
uv run nuclear-war source-evidence-draft-stubs --kind expansion-composition
```

Generated stubs are capture aids only. Replace their TODO fields and generic `private/` references
from physical-copy or publisher-authorized source work before any promotion attempt.

## Capture Rules

- Photograph card fronts and backs, rules sheets, spinner, mats, and population cards.
- Store private photos outside the public repository.
- `research/source_evidence/private/` is ignored as a local safety net only.
- Record private file references only, such as `private/source-capture/card-front.jpg`.
- For `evidence_kind: "physical_copy"`, validators require source references to start with
  `private/`.
- Do not include exact card text, official text, unofficial text, art, or image filenames that expose
  rights-restricted material.
- Use `verification_status: "draft"` for first-pass capture.
- Use `verification_status: "second_pass_verified"` only after a second pass confirms the count,
  card identity, and derived effect summary.
- Set `verified_by_second_pass` to `true` only for second-pass verified records.
- Keep publisher replies and authorization correspondence outside the public repository.
- Treat official public download URLs as source leads until draft records pass preflight and
  second-pass review.

## Registry Update Boundary

These manifests are intake evidence. They do not change runtime rules by themselves. After evidence
is present and validation passes, make registry card-effect or expansion count changes in a separate
rules-change branch with focused tests.
