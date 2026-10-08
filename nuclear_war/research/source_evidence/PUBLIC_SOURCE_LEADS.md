# Public Source Leads

This inventory lists current public source leads for source workers. It is not source evidence,
and it does not create live manifests, draft records, registry changes, or permission by itself.

The leads below are already indexed in the imported source bundle at
`research/imports/2026-06-14_nuclear_war_card_game_research_bundle/source_index.json`.
Verify each URL before using it in source work.

## Official Public Leads

| Source ID | Lead | URL | Public-safe use |
|---|---|---|---|
| `OFF-001` | Mr. B Games Nuclear Destruction product page | `https://www.mrbgames.com/products/pre-order-nuclear-destruction-card-game` | Product context, publisher contact path, and official download links. |
| `OFF-002` | Nuclear Destruction updated rules PDF, Apr. 2 2026 | `https://cdn.shopify.com/s/files/1/0040/1240/8885/files/NucDesRulesUpdated040226.pdf?v=1775165495` | Modern edition rules, component boundaries, setup, turn structure, and edition context. |
| `OFF-003` | Nuclear Destruction anti-missile chart PDF | `https://cdn.shopify.com/s/files/1/0040/1240/8885/files/Nuclear_DestructionAntiMissileChart.pdf?v=1775165495` | Modern anti-missile and evasion chart context. |
| `OFF-004` | Nuclear Destruction game log PDF | `https://cdn.shopify.com/s/files/1/0040/1240/8885/files/NuclearDestructionLog.pdf?v=1775165495` | Play-aid context for future modern-edition traces or reports. |

## Evidence Boundary

- These leads do not create `card_effect_evidence.jsonl` or
  `expansion_deck_composition.jsonl`.
- They do not clear `card_effect_transcription`, `expansion_deck_composition`,
  `expansion_rules_verification`, or `nuclear_destruction_modern` blockers.
- Do not copy exact card text, scans, art, PDF pages, or private correspondence into this
  repository.
- Public PDF URLs can be recorded as source references for publisher-hosted public materials only
  when the derived record has passed draft preflight and second-pass review.
- Publisher authorization is still required before using non-public publisher material or private
  correspondence as a source.

## Workflow

1. Check the product page and download URLs before a capture session.
2. Use these public leads to decide what source work can be done from public materials and what
   still requires a physical copy or publisher authorization.
3. Draft records outside the live manifest names first.
4. Run `nuclear-war validate-source-evidence` on explicit draft paths.
5. Promote only second-pass verified records into live manifest names.
