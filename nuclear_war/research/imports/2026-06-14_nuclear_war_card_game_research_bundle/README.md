# Nuclear War card game research bundle

Created for building a research-grade simulation of Douglas Malewicki's *Nuclear War* card game family.

This bundle collects public-source notes, structured source indexes, rule summaries, card inventories, variant notes, and simulation schema for continuing the reconstruction work.

Downloaded PDFs and their extracted text are not redistributed in this repository. The source URLs are listed in `source_index.csv`.

## Important legal/provenance note

This is a research bundle. It distinguishes:

- **Official/current materials**: presently hosted by Mr. B Games for *Nuclear Destruction*, the current Nuclear War-family release.
- **Official-derived or public mirrors**: rules/card-list/FAQ material found on third-party sites. These may preserve older Flying Buffalo-era text but are not necessarily hosted by the current rights holder.
- **Community/fan material**: BoardGameGeek wiki notes, postal-play rules, player guides, Tabletop Simulator implementations, and combined-rule compilations.
- **Tertiary/contextual material**: Wikipedia, reviews, museum records, news articles, and nuclear-wargaming scholarship.

Exact card wording and card art remain rights-restricted. For simulation, use the `effect_summary` fields and replace them with verified exact card text only from your legal physical copy or publisher-authorized sources. Do not redistribute card art or full card text without permission.

## Most useful folders

- `99_sources/source_notes/` - notes for sources that could not be downloaded as raw HTML/PDF.
- `source_index.csv` / `source_index.json` - full source catalog.
- `03_card_data/` - structured card inventories and confidence notes.
- `04_simulation_model/` - state model, rules engine spec, randomizer tables, and variant modules.
- `07_gaps_and_next_steps/` - exact-text and edition-reconciliation checklist.

## Captured source materials

Downloaded during research (not redistributed here):

1. Official Mr. B Games *Nuclear Destruction* rules PDF.
2. Official Mr. B Games *Nuclear Destruction* anti-missile chart PDF.
3. Official Mr. B Games *Nuclear Destruction* game log PDF.
4. Public mirror of a later/base *Nuclear War* rules PDF using two ten-sided dice.
5. Public scan of an older spinner-era *Nuclear War* rule sheet.

HTML pages and dynamic sites were captured as URL-indexed source notes rather than raw HTML because the downloader available in this environment reliably fetched PDFs but not HTML pages.

## Recommended workflow

1. Use `source_index.csv` to identify the source you want.
2. Use `02_rules_and_variants/rules_reconstruction_summary.md` for the unified rules map.
3. Use `03_card_data/base_game_card_inventory.csv` as the first-pass base deck manifest.
4. Use `04_simulation_model/rules_engine_spec.md` and `04_simulation_model/spinner_and_die_tables.json` to implement rules.
5. Use `07_gaps_and_next_steps/exact_text_gap_list.md` when transcribing exact text from your physical copy.
