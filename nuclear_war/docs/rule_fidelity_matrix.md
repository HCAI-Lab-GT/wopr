# Nuclear War Rule Fidelity Matrix

This page tracks what the current deterministic engine covers against the
rules sources. I use it as the audit companion to `docs/v1_acceptance.md`.

## Active Card Registry

The active v1 registry is `rules/nuclear_war_base_cards.jsonl`.

The imported research bundle at
`research/imports/2026-06-14_nuclear_war_card_game_research_bundle/` is source
evidence, not direct runtime data. I use it to track source priority, edition
conflicts, and card-inventory leads.

The bundle contributes `source_index.csv`, `source_index.json`,
`03_card_data/base_game_card_inventory.csv`,
`04_simulation_model/rules_variants.json`,
`04_simulation_model/spinner_and_die_tables.json`, and
`07_gaps_and_next_steps/exact_text_gap_list.md` as v1 specification inputs.

The active registry uses imported bundle source-index IDs in its `sources`
fields. `nuclear-war validate-rules` loads IDs from `source_index.json` and
requires empty malformed JSONL, IDs/names/types, duplicate IDs, unresolved labels,
invalid counts, and metadata-only deck counts.

Current card families are warheads, delivery systems, propaganda,
anti-missiles, secrets, top secrets, postal special metadata records, postal
carrier metadata for MX Missile, and postal special metadata for Supervirus.

The postal special records use `count_in_deck=0` because the imported research
bundle does not prove expansion deck counts. They bind implemented mechanics to
registry records and source notes without changing the default base deck.

## Active Edition Variant

The active runtime variant is `base_later_two_d10`.

`nuclear-war validate-rules` reports hand draw target 10, population deck size model 40 cards,
randomizer `base_two_d10_fallout_chart`, two initial face-down cards, anti-missile turn jump
enabled, no expansion sets, no special powers, no trading, press disabled, and simultaneous orders
disabled.

New game states store this variant id to distinguish the current default from
future classic-spinner, Nuclear Destruction, postal-press, or expansion variants.

## Implemented Base Effects

- Secret and top-secret cards enter the secret pipeline when drawn.
- Postal stolen secrets wait until the following postal turn before resolving.
- Secret and top-secret effect keys are validated by `nuclear-war validate-rules`.
- Registry validation reports restricted exact-text fields and the active
  registry uses effect summaries instead of unofficial card text.
- Registry validation reports postal special effect tags and fails when an
  implemented postal special family is missing from the active registry.
- Draw-to-target accounting counts hand cards, face-down queue cards, and
  deterrent cards while excluding the face-up slot.
- Population steal, population gain, population damage, population removal, and
  skip-turn effects are implemented.
- Population loss and gain make change against the population bank in the
  physical card denominations {1, 2, 5, 10, 25}. When the combined player and
  bank cards cannot compose the exact target total (possible in 5-6 player
  games, where the deal leaves only 4-5 bank cards), the target is rounded
  down to the largest composable total: the player loses slightly more, or
  gains slightly less, than the nominal amount, never the reverse. The
  fallback is deterministic, conserves the 240M deck total, and reports the
  actually applied delta in replay events. A round-down to zero population
  eliminates the player. Migration-style effects (propaganda and secret
  steals) cap the mover's gain request at the card's nominal value, so a
  round-down that makes the target's loss heavier never inflates the steal;
  the extra loss stays in the bank and is not a separate event field —
  replays re-simulate it deterministically from the seed.
- Propaganda uses registry population values and only affects population while
  peace is active.
- Postal no-press legal actions can queue base propaganda, secret-target,
  secret-theft, defense, sabotage, cruise launch/move/drop, submarine setup/use,
  atomic setup/use, space setup/use, Space Shuttle attack/reload, killer
  satellite launch/attack, Supervirus start/pass, final-strike targeting, and
  peace-vote orders.
- Delivery systems reject warheads above their registry max yield.
- Bombers can load multiple warheads up to their registry payload, and a table
  bomber attacks in multiple successive turns: after a resolved attack the
  bomber stays on the launch track with its dropped megatons tracked against
  the payload, until the payload is exhausted, an anti-missile shoots it down,
  the fallout chart's out-of-fuel band spends it, or the next face-up card is
  not a warhead or exceeds the remaining payload. Attacking with an armed
  warhead stays mandatory, as the rules require.
- Anti-missile labels are checked against delivery intercept metadata.
- Table anti-missile intercepts make the defender next in envs and simulation.
- Fallout spinner effects are applied during launch resolution.
- Fallout spinner events log the active randomizer and source table id for
  replay auditability.
- Postal equipment events that use the same randomizer log the active
  randomizer and source table id for replay auditability.
- Replay event records include turn numbers so events can be audited against
  action chronology.
- Replay validation rejects action and event turns outside the stored game turn
  range.
- Rule validation reports a source-linked `rules_trace` scaffold for current
  table replay action and event families, plus a source-mapped `rules_trace_steps`
  catalog for the step IDs those records reference.
- Rule validation reports a bounded `rules_trace_full_game` summary for a deterministic
  full table replay. The semantic trace maps each replay action and event to a
  source-mapped rule step and reports no full-game trace gaps.
- Warhead target declarations end peace and mark all players at war even when
  the delivery is later sabotaged, intercepted, duds, or misfires.
- Smart Bomb launch orders double 10 or 20 megaton warheads before spinner
  modifiers. This is engine-level resolution only; no legal action produces a
  smart-bomb order in real play (see Current Rule-Fidelity Limits).
- Final strike is scheduled after population elimination by warheads or secret
  damage effects, with postal targeting exposed as a legal action. A player who
  eliminates themselves through a booster-explodes backfire — or a space-platform
  launch-pad crash (see below) — also gets final retaliation, matching the rule
  that any death by warhead grants it (only a propaganda defeat forfeits it).
- The final-retaliation card pool combines built launch orders with the
  delivery and warhead cards from the hand, the face-down queue, and the
  deterrent slots, in that pool order, before the parked final-strike cards.
- Postal cruise missiles can launch, linger over a target, drop on that target,
  move to new targets, and return to sender for missing move orders or moves to
  already visited countries. A return-to-sender missile force-drops on its
  owner the following turn; no new move or drop order can recall it, and the
  doomed missile offers no legal actions.
- Postal submarines can be sent to sea with valid 10 or 20 megaton warheads,
  stay in port without a valid warhead, reload from port, fire their carried
  warhead, become exposed while returning to port, or return to port without
  exposure. An exposed returning submarine automatically makes port during the
  following submarines phase unless it was destroyed while exposed, so the
  fire, exposed, port, reload cycle is closed.
- Postal anti-missile defense is a conditional order: a player holding an
  anti-missile card may order it held against incoming launches before any
  target is known. The card stays in hand until it actually intercepts, and
  unused orders expire at the end of the turn. Postal launch resolution and
  postal final strikes intercept only through these orders; the table-mode
  automatic hand intercept does not apply in postal play.
- Postal atomic cannons can be set up with one ready cannon limit, persist as
  ready equipment, fire a 10 megaton warhead through the fallout spinner,
  reposition to another player, reject other warhead yields, fire through
  explicit final-retaliation orders that only tests queue today, and be
  destroyed by launchpad backfire.
- Launch orders can target atomic cannons or exposed submarines instead of
  population. Dud or backfire spinner outcomes leave the equipment intact.
  This is engine-level resolution only; no legal action produces an
  equipment-target order in real play (see Current Rule-Fidelity Limits).
- Postal space platforms can launch with stored warheads, consume one stored
  warhead per drop, remain aloft while warheads remain, and crash into the
  owner on double launch failure. A crash that drains the owner's last
  population eliminates them like any other warhead death: it logs
  `player_eliminated`, marks peace-restore pending, and pools their remaining
  launch cards into a final strike. Attribution decision: a launch has no
  target, yet the replay schema forbids both a self and a null `by`, so V1
  attributes the crash-death to the owner's top living opponent — the same
  country the pooled final strike targets, keeping `by == eliminated_by == the
  retaliation target`. If the crash makes the owner the last casualty (no living
  opponent), attribution falls back to another (dead) seat so the event stays
  replay-legal. Space platforms are expansion-only and absent from the default
  postal deck, so this path is unreachable in the parity sweeps and only fires
  under injected orders.
- A player eliminated earlier in a turn does not execute its queued equipment or
  action orders. Every postal equipment/action handler (space platform, submarine,
  atomic cannon, cruise, killer satellite, space shuttle, supervirus, sabotage)
  skips a dead owner, and the space-platform handler additionally rechecks owner
  aliveness after its launches so a double-cloud self-crash cannot still drop. The
  lone exception is the atomic-cannon final-strike path, which deliberately fires
  FOR the eliminated retaliating player. This equipment is expansion-only, so the
  guard is byte-identical in the default table and postal sweeps.
- Space Shuttle reload orders can add warheads to an existing launched space
  platform.
- Space Shuttle attack orders can resolve as direct attacks without requiring
  an existing launched space platform.
- Postal killer satellites can launch to orbit, attack enemy space platforms,
  destroy both satellite and platform on success, and discard only the satellite
  on launch-cloud failure.
- Sabotage can block missile or bomber launches, atomic cannon fire orders, and
  killer satellite launch orders.
- Sabotage can block direct Space Shuttle attack orders.
- Pure-engine postal play (the `execute_postal_turn` path used by `simulation.py`
  and `env_postal.py`) fires phase-3 final strikes at a deterministic target: a
  hand-assembled retaliation order left untargeted is pointed at the eliminator if
  still alive, else the highest-population living opponent — reusing the same policy
  the decision-loop path drives via the `FINAL_STRIKE_TARGET` action. Previously
  such orders were silently dropped by `execute_launches` (which skips
  `target_id is None`), so pure-engine postal never fired them.
- Fallout target adjustments use the same million-population units as player
  population records.
- Peace is restored after an eliminated player has no pending final strike, but
  only when peace had actually been broken. A non-attack kill at peace — a secret
  effect, or a space-platform launch-pad crash — marks peace-restore pending
  without declaring war; at peace the pending flag is cleared silently and no
  phantom `peace_restored` is emitted. When peace was broken, restoration clears
  both the global peace flag and every player's war flag.
- The opening face-down commitment is an agent decision (2026-07-02): the
  table decision loop pauses on one `SETUP_PLACE` decision per empty opening
  slot per player (seat order, options in hand order) before the first turn,
  matching the printed "the player is now committed to a specific strategy"
  choice. `options[0]` reproduces the old auto-commit of `hand[:2]` exactly,
  so heuristic goldens are unchanged; random-agent seeded outcomes
  intentionally diverged (asserted by
  `test_random_table_outcomes_diverged_after_setup_peace_fidelity`). Postal
  setup keeps the auto-commit pending its own decision surface.
- Peace-restoration strategy replacement is implemented (2026-07-02) as the
  table `STRATEGY_REPLACE` decision: when peace is restored, each living
  player may replace one or two face-down cards with hand cards, or decline
  (decline is `options[0]`, so pick-first baseline agents keep the legacy
  no-replacement behavior and heuristic goldens stay pinned). The card already
  turned face up is not replaceable, per the printed rule. The rules do not
  say where the displaced face-down card goes; the engine returns it to the
  player's hand (documented modeling choice). The window opens immediately at
  the restoration, even mid-turn (the printed rules give no timing beyond
  "when peace is restored"). Random-agent seeded outcomes intentionally
  diverged (same divergence golden as above).
- Postal peace votes restore peace only when every player votes for peace.
- MX Missile launch orders can carry one warhead larger than 10 megatons, reject
  10 megaton warheads, and resolve one Radioactive Fallout die roll per 10
  megaton segment: a non-cloud roll destroys 2 million plus the die face
  (4 to 8 million), and a nuclear cloud ("explodes on launchpad") cancels only
  that one segment with no damage and no attacker backfire.
- Supervirus orders can start an infection, apply the postal-adjusted nuke die
  loss, pass to a valid live country, reject a pass back to the previous source
  while more than two countries survive, confer immunity after four retained
  turns, and clear when the holder is eliminated. Immunity is enforced: an
  immune country cannot be infected again by a start order, passes to an
  immune country fail and the holder retains the virus, and immune countries
  are excluded from supervirus start and pass legal actions.

## Postal No-Press Handling

- Press remains disabled in v1 no-press mode.
- Postal phase ordering is represented in code and validated for required phase
  names.
- Non-communication phases operate on deterministic pending orders.

## Current Rule-Fidelity Limits

⚠️ Expansion-card postal mechanics are registry-backed metadata only. The active
registry does not prove expansion deck counts, exact card names beyond local
source notes, or exact printed text. I should not include those cards in the
default base deck until a physical copy or authorized source verifies counts.

⚠️ Some local registry records have low or medium confidence source notes.
Resolved source-index IDs do not turn those effects into verified exact text.

⚠️ The imported research bundle confirms that source editions disagree on
population deck size, randomizer model, hand target, anti-missile turn jump,
special powers, trading, and no-press status. V1 reports those fields in its
active `base_later_two_d10` payload, but alternate edition modules remain
unimplemented.

⚠️ Supervirus is implemented from the postal rules as a metadata-backed
mechanic, but expansion count, exact printed text, and superserum identity
remain unverified.

⚠️ Superserum removal is engine-level only. The resolver consumes a
`supervirus_serum` pending order, but no card identity is verified and no
legal action produces that order, so a supervirus cannot be cured in real
play. This stays a known limit until a physical copy or authorized source
verifies the superserum card.

⚠️ Smart Bomb is engine-level only. Launch resolution doubles eligible
warheads when an order carries `smart_bomb`, but the Smart Bomb registry
record is metadata with `count_in_deck=0`, so the card can never be drawn and
no legal action sets that order field. The mechanic is unreachable in real
play until source evidence enables the expansion deck count and an action
producer is added.

⚠️ Equipment targeting (nuking an atomic cannon or exposed submarine instead
of population) is engine-level only. Launch resolution consumes an
`equipment_target` order field, but no legal action produces it, so the
postal "Targeting the Atomic Cannon or a Submarine" rule is unreachable in
real play. Wiring it needs a new targeting action registered with the replay
validators.

⚠️ The semantic rules trace covers one deterministic full table replay against
source-mapped rule-step IDs. It does not verify exact card text, expansion deck
composition, alternate editions, or postal press adjudication.

⚠️ The inexact-change round-down for thin 5-6 player population banks is a
deterministic engine policy, not a source-backed rule. The printed rules do
not specify how to settle population amounts the bank cannot change exactly;
a physical table resolves this by negotiation. Round-down was chosen over
round-to-nearest to match the punitive spirit of the game (losses land
heavier, gains land lighter). 3-4 player seeded outcomes are unaffected
because exact change always exists there; that invariant is pinned by the
goldens in `tests/integration/test_decision_loop_parity.py`.

Postal equipment launch resolution rolls the 6-sided Radioactive Fallout die
(`roll_fallout_die`: a plain uniform d6 where face 1 is the nuclear cloud, a
launch failure, and 2 through 6 succeed). Each roll is logged as a
`fallout_die_result` replay event whose `randomizer` and `source_table_id` are
`postal_radioactive_fallout_die`, distinct from the two-d10
`base_two_d10_fallout_chart` spinner. The affected resolutions are space
platform launch, cruise missile launch, killer satellite attack, and the
per-segment rolls of the MX missile. A space platform launch that rolls a cloud
loses the platform and its warheads and rolls again; a second cloud crashes the
platform into the owner for 10 million. The MX destroys 2 million plus the die
face per non-cloud 10-megaton segment, and a cloud cancels only that segment.
The launch-failure probability is now the rules' one-in-six rather than the
spinner's 5 percent, and the plain success/cloud roll replaces the full fallout
chart on these launches. Space shuttle direct attacks are deliberately excluded:
the postal rules give the shuttle no Radioactive Fallout die and describe it as
carrying a warhead "just like a missile", so it detonates through the two-d10
nuking spinner like any other missile. Submarine fire and atomic-cannon fire
likewise stay on the nuking spinner (2026-07-01 audit). The change intentionally
diverges postal seeded outcomes wherever this equipment is launched, asserted at
the scenario level in
`tests/integration/test_postal_fallout_die_parity.py` (e.g. seed 2 turns a
launched space platform into a crash and an MX 20-megaton strike from 4 to 11
million); RNG consumption shifts from the die roll onward, so replay event
ordering and draw counts move after the first equipment roll.

⚠️ The four Radioactive Fallout die mechanics are reachable only through
directly-injected postal equipment orders (and expansion registry metadata):
space platforms, cruise missiles, killer satellites, and the MX are
expansion-only cards absent from the default postal deck, so no default-agent
sweep game launches them and the 240-game postal sweep stays byte-identical
(also asserted in `test_postal_fallout_die_parity.py`). Wiring the expansion
deck composition so these fire in real play is separate future work.

⚠️ Table final-strike targeting points every untargeted retaliation order at
one policy-chosen target, where the rules announce a target for each separate
delivery system. Postal submarine and space-platform final-strike fire is
absent. The atomic-cannon final-fire path exists in `final_strike`, but no
production action queues it; only tests exercise it.

⚠️ Parked opening secrets resolve on each player's first turn instead of
during the printed opening round. Decided 2026-07-02: kept as a deliberate
deferral. The opening-round resolution contains no agent choice the engine
does not already surface (secrets auto-resolve; offensive targets pause as
SECRET_TARGET decisions), and first-turn resolution keeps every resolution
event — including an opening elimination — inside the replay turn log. Moving
it into setup would reorder every seeded draw for no new decision content.

⚠️ The face-up card resolves during the SLIDE phase, before the DETERRENTS and
PLACE phases, where the printed turn order resolves it in step 4, after PLACE.
Decided 2026-07-02: kept as a deliberate deferral. Reordering resolution after
PLACE changes what the player knows at deterrent/placement time in every turn
of every game, invalidating the entire parity lineage and all goldens
at once; if taken, it must be its own fidelity fix with a full golden refresh.

⚠️ Postal deviations beyond the Radioactive Fallout die resolution above:
Supervirus damage uses the postal-adjusted nuke die (2 counts as 1, 6 counts as
5) where the postal rules roll the uniform Radioactive Fallout die with the
cloud counting as 1 (supervirus does not use the `roll_fallout_die` helper). The optional nuke-die roll after the spinner in phase 9 is not
implemented. Cruise missiles require and consume a hand warhead at launch,
though the rules describe them as self-contained carrier and warhead systems
that need no warhead. Killer satellites launch without the Titan or Atlas
missile the rules require. Space Shuttle direct attacks have no 50 megaton cap
and cannot be intercepted. The population deal uses the base-edition table and
rejects player counts above six, while the postal document lists its own deal
table and supports seven and eight players. Equipment specials are played from
hand rather than exposed from the face-down queue, and specials or propaganda
flipped from the queue are plain-discarded with no effect.
