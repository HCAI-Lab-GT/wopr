# Source Evidence Capture Checklist

This checklist is not source evidence. It lists public-safe target IDs that source workers should
cover when creating draft source-evidence records. Do not include exact card text, official text,
unofficial text, art, scans, or private working notes in this file or in live manifests.

Use this checklist with `CAPTURE_RUNBOOK.md`, `card_effect_evidence.template.jsonl`, and
`expansion_deck_composition.template.jsonl`.

## Card-Effect Targets

These active registry cards have `count_in_deck > 0`. Capture derived effect evidence and counts in
draft `card_effect_evidence` records only after physical-copy or publisher-authorized material is
available.

| card_id | card_name | card_type | count |
|---|---|---:|---:|
| `nw_base_f135174f` | Warhead 10 Mt | warhead | 19 |
| `nw_base_63d00850` | Warhead 20 Mt | warhead | 10 |
| `nw_base_5baf79b7` | Warhead 50 Mt | warhead | 4 |
| `nw_base_a2109e47` | Warhead 100 Mt | warhead | 1 |
| `nw_base_b3a2b1d5` | Propaganda 5M | propaganda | 12 |
| `nw_base_ce2c2080` | Propaganda 10M | propaganda | 6 |
| `nw_base_e81625f2` | Propaganda 25M | propaganda | 2 |
| `nw_base_817ae772` | Polaris Missile | carrier | 9 |
| `nw_base_782a2d4e` | Atlas Missile | carrier | 9 |
| `nw_base_17d18cbc` | B-70 Bomber | carrier | 6 |
| `nw_base_524da209` | Saturn Missile | carrier | 3 |
| `nw_base_68e841fd` | Anti-Missile (P) | anti_missile | 1 |
| `nw_base_635d7044` | Anti-Missile (A) | anti_missile | 1 |
| `nw_base_b0c93572` | Anti-Missile (S) | anti_missile | 1 |
| `nw_base_00bc504e` | Anti-Missile (B) | anti_missile | 1 |
| `nw_base_b6794c74` | Test Ban | secret | 1 |
| `nw_base_25ca25d8` | Summit Talk | secret | 1 |
| `nw_base_a82055e8` | Stock Market Super Boom | secret | 1 |
| `nw_base_9c4a685d` | Peace Corps | secret | 1 |
| `nw_base_5df64089` | First on Moon | secret | 1 |
| `nw_base_4f7e97eb` | Beatnik Pacifists | secret | 1 |
| `nw_base_1a3dc61e` | Population Explosion | secret | 1 |
| `nw_base_88397cd6` | Little Old Ladies | secret | 1 |
| `nw_base_73c4d9d1` | Raises Taxes | secret | 1 |
| `nw_base_1e921213` | Ambassador Gets Drunk | secret | 1 |
| `nw_base_9c57e2d6` | Disastrous Earthquake | top_secret | 1 |
| `nw_base_59743030` | 10 Million Leave for a Neutral Country | top_secret | 1 |
| `nw_base_bdab30a4` | Supergerm | top_secret | 1 |
| `nw_base_f22d41be` | Mysteriously Vaporized | top_secret | 1 |
| `nw_base_cef59053` | Violent Tornado | top_secret | 1 |

## Expansion Composition Targets

These expansion mechanic registry IDs require composition evidence before any expansion
`count_in_deck` value can be enabled.

| registry_id | postal_effect | supported_modes |
|---|---|---|
| `nw_postal_atomic_cannon` | atomic_cannon | postal |
| `nw_postal_cruise_missile` | cruise_missile | postal |
| `nw_postal_killer_satellite` | killer_satellite | postal |
| `nw_postal_mx_missile` | mx_missile | postal |
| `nw_postal_saboteur` | sabotage | postal |
| `nw_postal_smart_bomb` | smart_bomb | postal |
| `nw_postal_space_platform` | space_platform | postal |
| `nw_postal_space_shuttle` | space_shuttle | postal |
| `nw_postal_submarine` | submarine | postal |
| `nw_postal_supervirus` | supervirus | postal |

## Use Boundary

- Use `nuclear-war source-evidence-targets` for machine-readable public-safe target metadata.
- Use `validate-source-evidence` on draft files before promotion.
- Use the target-detail payloads from draft preflight to inspect missing and unverified target
  queues.
- Keep physical-copy references under `private/`.
- Promote only second-pass verified draft records into live manifest names.
- Make registry effect or expansion count changes in a separate branch after live manifests pass.
