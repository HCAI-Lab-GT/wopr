# Nuclear War card game research report

## Scope

This report gathers sources for studying and simulating *Nuclear War* by Douglas Malewicki, including official current materials, classic/base rule mirrors, older spinner-era scans, card inventory sources, PBM/press variants, expansion leads, and context sources.

## Best source set

1. **Official current family rules** - Mr. B Games *Nuclear Destruction* product page and PDFs.
2. **Classic/base rules** - Goblins.net *Nuclear War Game Rules* PDF mirror.
3. **Older spinner-era rules** - Magisterrex/WordPress scanned two-page rule sheet.
4. **Card inventory** - BoardGameGeek moreinfo and Scribd card list.
5. **Rules clarifications** - Scribd FAQ.
6. **Press/PBM variant** - VariablePig postal rules.
7. **Context/history** - LA Times, ICv2, museum records, Origins Hall of Fame, InsideGMT.

## Main reconstruction status

The general game system is reconstructable with high confidence:

- population-based win/loss;
- propaganda vs nuclear attack paths;
- launch-track delayed commitment;
- delivery systems + warheads;
- anti-missile defense;
- random fallout/malfunction tables;
- peace/war mode;
- final retaliation chains;
- everyone-can-lose ending.

The exact text of all cards is not fully verified from authoritative online sources. The current working model should use `effect_summary` fields until the physical copy is transcribed.

## Edition conflicts to track

- Older sources use a physical spinner; at least one base rules mirror uses two ten-sided dice.
- Older scan/card-list sources reference a 40-card population deck; the Goblins base rules mirror says 20 population cards.
- Current *Nuclear Destruction* has six-player standalone support, a Nuclear Escalation die, updated anti-missile chart, optional rules, and booster integration guidance.
- Fan/community combined rules may make assumptions that do not match any one official printing.

## Recommendation

Build the simulator in two layers:

1. **Rules kernel**: generic Nuclear War mechanics with configurable variants.
2. **Edition modules**: classic spinner, later two-d10 base, Nuclear Destruction modern, PBM press, no-press house, combined expansions.

Then transcribe the user's physical copy into a private exact-text manifest and map each card to the rules kernel.
