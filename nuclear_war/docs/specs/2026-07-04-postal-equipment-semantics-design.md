# Postal equipment / final-strike / peace-restore semantics: design

**Date:** 2026-07-04

## Context

An adversarial review of the space-platform crash-kill elimination change surfaced three
pre-existing semantics issues in postal play. All three were **verified against the
current code** and their default-play blast radius **measured empirically** (probes over
players {3,4} × agents {heuristic,random} × seeds 1..20, both modes):

| Issue | Confirmed | Default-play reach | Re-baseline |
|-------|-----------|--------------------|-------------|
| 1. Dead owner still executes queued equipment orders | yes | **none** — equipment absent from default deck (byte-identical) | no |
| 2. Untargeted postal final strikes silently dropped in pure-engine | yes | **44/80 postal games change** (rides on `secret_effects` + warhead kills, both default deck) | **postal** |
| 3. Spurious `peace_restored` on a peacetime non-attack kill | yes | **7/80 postal games** (table 0/80) | **postal (event-log only)** |

> Only Issue 1 is expansion-only (unreachable in default play).
> Issues 2 and 3 change the **default** postal goldens by design.

## Decisions

- **Issue 2:** Fix — auto-assign a deterministic final-strike target in the pure-engine
  postal path; accept the 44/80 change; full postal re-baseline.
- **Issue 3:** Fix — guard the emission on "peace was actually broken"; postal re-baseline.
- **Scope:** All three fixes together, with **one combined postal re-baseline**.

## Non-negotiable invariants (the parity gate)

The gate is a **full-result hash including the event log**, across players {3,4} ×
agents {heuristic,random} × seeds 1..60, for **both** modes (480 games).

- **Table sweep hash: UNCHANGED vs HEAD.** All three fixes are table-byte-identical
  (Issue 1 = equipment absent; Issue 2 = `phase_final_strike` is postal pure-engine only;
  Issue 3 = 0/80 table spurious restores). This is a hard invariant — any table drift is a bug.
- **Postal sweep hash: CHANGED vs HEAD, and the diff must be fully explainable** as
  (a) hand-assembled final strikes now firing (Issue 2) and (b) removed phantom
  `peace_restored` events (Issue 3). Re-baseline the postal artifacts after confirming.

Baseline captured on HEAD **before** any change: dump both sweeps (with events) to artifacts
and record their hashes, so the post-change comparison is exact.

---

## Issue 1: Dead owner still executes queued equipment orders

### Root cause
`apply_space_platform_orders` (`engine/postal/space_platform.py:27`) runs `_launches`
then `_drops` for the same player with no owner-alive recheck. If the owner is
crash-killed in `_launches` (double-cloud, `:78-87`) and also has a `space_platform_drop`
order, `_drops`/`_drop` still spins, calls `declare_war`, and damages a target
(`:150-184`). `_drops` guards only the **target** (`:142`), never the owner. All seven
sibling handlers share the `for player … pop orders` shape with **no owner-alive guard**
(every `.alive` check is a *target* check).

### Death modes (verified)
- **Intra-iteration self-kill:** only `space_platform` (crash). killer_satellite removes
  platforms not population; submarine/atomic_cannon/cruise/space_shuttle fire at targets
  and self-destruct only the *equipment*, never the owner.
- **Cross-actor within a phase:** actor A's equipment kills actor B earlier in the loop
  (or an earlier handler in the same phase, e.g. shuttle→platform→satellite); B then acts
  while dead. Applies to all handlers.

### Fix
A **consistent owner-alive guard**: a dead actor does not execute its equipment orders.
- Each per-player equipment handler skips a dead owner at the top of its loop
  (`if not player.alive: continue`). This covers cross-actor deaths (checked at
  iteration time, so intra-phase kills are caught).
- `space_platform` additionally **rechecks owner-alive between `_launches` and `_drops`**
  (its unique intra-iteration self-kill).
- **`atomic_cannon` carve-out:** `apply_atomic_cannon_orders` is reused by the
  final-strike path (`engine/final_strike.py:_run_atomic_cannon_orders`) where the actor
  is *intentionally* dead (retaliation). The guard is therefore **parameterized**
  (e.g. `apply_atomic_cannon_orders(state, skip_dead_owners=False)`): the equipment-phase
  caller (`phase_submarines`) opts in with `skip_dead_owners=True`; the final-strike
  caller keeps the default and still fires for the dead owner.

### Parity
Byte-identical in default table + postal sweeps (equipment produces 0 events there).
Verified by the unchanged-hash invariant on both modes.

### Tests (TDD, `tests/unit/test_space_platform.py` + sibling handler tests)
- Owner crash-killed in `_launches` with a queued `space_platform_drop` ⇒ **no**
  `space_platform_dropped`, **no** extra `declare_war`, target undamaged.
- Cross-actor: A's equipment kills B earlier in a phase; B's queued order does **not**
  resolve.
- `atomic_cannon` final-strike path still fires for the eliminated owner (regression guard
  for the carve-out).

---

## Issue 2: Untargeted postal final strikes silently dropped in pure-engine

### Root cause
`schedule_final_retaliation` (`engine/launch_helpers.py:137`) in non-TABLE mode queues
`pending_orders['final_strike']` and returns `[]`; hand-assembled orders carry
`target=None` (pooled in-flight launches keep their original target). `assign_retaliation_targets`
is gated to TABLE (`:190-193`). Next, `phase_final_strike` → `run_final_strike` →
`execute_launches` skips any order with `target_id is None` (`engine/launch.py:61`), so the
pooled retaliation is dropped. Callers include `launch_resolution.py` (regular warhead kills)
and `secret_effects.py` — **both default deck**, hence the 44/80 default-postal reach.

The decision-loop (LLM) path is unaffected: it assigns targets via the
`FINAL_STRIKE_TARGET` action and never calls `execute_postal_turn`/`phase_final_strike`
(verified: 0 references in `decision_loop.py`).

### Fix
In `phase_final_strike` (`engine/postal/handlers_early.py:69`), **before** `run_final_strike`
consumes the orders, assign a deterministic target to any still-untargeted order by reusing
`assign_retaliation_targets(state, player.player_id, orders, eliminated_by)`, where
`eliminated_by` is read from the orders (each order carries `order['eliminated_by']`,
set at schedule time). Policy is the existing V1 one: strike the eliminator if still alive,
else the highest-population living opponent. Pooled orders that already have a target are
left untouched (assign only fills `warheads and not target`).

Fix site rationale: `phase_final_strike`/`execute_postal_turn` are pure-engine only
(`simulation.py`, `env_postal.py`); the decision-loop path has its own sequencing. Assigning
at fire time (phase 3) mirrors when the decision-loop agent is prompted to target, and uses
current populations for the highest-pop tiebreak.

### Parity
Changes the postal sweep (44/80 in the 80-game probe).
Table unchanged. Re-baseline postal after confirming the diff is only newly-firing retaliation.

### Tests (TDD)
- Pure-engine postal (`execute_postal_turn`): a hand-only elimination schedules a final
  strike that **fires** at a deterministic target (eliminator-first, else highest-pop),
  producing retaliation damage.
- The assignment does **not** override a pre-targeted pooled order.
- Decision-loop postal path unchanged (a `FINAL_STRIKE_TARGET`-driven test still passes;
  no new auto-target leaks in).

---

## Issue 3: Spurious `peace_restored` on a peacetime non-attack kill

### Root cause
`restore_peace_after_completed_eliminations` (`engine/war_state.py:33`) clears
`PEACE_RESTORE_PENDING` and calls `restore_peace` + (via callers) emits `peace_restored`
whenever a pending player has no pending final strike — **without checking whether peace
was ever broken**. Non-attack kills (`secret_effects.apply_secret_effect`, space-platform
crash) call `mark_peace_restore_pending` at peace (no `declare_war`), so a peacetime kill
emits a phantom war→peace transition. `secret_effects` is default deck ⇒ 7/80 postal.

### Fix
In `restore_peace_after_completed_eliminations`, record `was_at_war = not state.peace`
after selecting the satisfied pending players. **Always clear** their `PEACE_RESTORE_PENDING`
flags (so no flag leaks). Then:
- `was_at_war` (peace was broken): `restore_peace(state)` and `return True` → caller emits.
- else (peace intact): `return False` → no `restore_peace`, no event.

Table stays byte-identical: a table elimination always follows an attack that declared war,
so `was_at_war` is always `True` there (probe: 0/80 table spurious).

### Invariant note
In default play, `state.peace is True` iff every player's `at_war is False` (they move
together via `declare_war`/`restore_peace`), so skipping `restore_peace` in the peace-intact
branch is a no-op. (Expansion equipment can set an individual `at_war` without `declare_war`, but that
is expansion-only and out of scope here.)

### Parity
Postal event-log-only change (7/80): removes the phantom event; touches no state, so
winners/populations are identical. Table unchanged. Folds into the same postal re-baseline.

### Tests (TDD, `tests/unit/test_war_declaration.py` / peace tests)
- Peacetime non-attack kill (secret effect drains a target to zero at peace) ⇒ **no**
  `peace_restored`, `PEACE_RESTORE_PENDING` cleared, `state.peace` still `True`.
- Wartime kill without final strike still restores peace and emits `peace_restored`
  (existing `test_table_peace_restores_after_elimination_without_final_strike` stays green).

---

## Interaction between fixes
Issue 2 makes final strikes fire, which `declare_war`; that changes peace state and thus
when Issue 3's guard applies. The combined behavior is captured by fixing all three, then
running **one** postal re-baseline and confirming the diff decomposes into the two intended
effects. Table remains a hard unchanged-hash gate throughout.

## Documentation
`docs/rule_fidelity_matrix.md` records:
- Dead actors do not execute equipment orders (owner-alive guard; atomic-cannon final-strike
  carve-out).
- Pure-engine postal now fires phase-3 final strikes at a deterministic target
  (eliminator-first, else highest-pop), consistent with the decision-loop path.
- `peace_restored` is emitted only when peace was actually broken.

## Out of scope
- Wiring the postal expansion deck itself.
- Expansion-only `at_war`-without-`declare_war` reconciliation.
- Any decision-loop / LLM-path behavior change.
