# Design Spec: Agent Decision Interface

Date: 2026-06-16.
Supersedes the deterministic V1 engine policies (they become *agent* logic, not engine
logic).

## 1. Goal & scope

Turn the Nuclear War engine into a **fully agent-driven, decision-point state machine** with
a clean **structured** interface, so every strategic choice is made by an agent
(heuristic / random / future-LM), on a faithful rules substrate. This is the foundation an
LM-agent experimental environment (Concordia) builds on.

**In scope:** agent decisions (every strategic decision becomes an agent choice via a
decision-point state machine) and observations (structured, hidden-info-safe per-agent
observations).

**Out of scope:** natural-language rendering / LM intent mapping (the Concordia harness);
new rules, expansions, editions; the LM agents themselves.

## 2. Core contract

Three pure engine entry points:

- `pending_decision(state) -> Decision | None` — the current choice (or `None` if terminal).
  Reads `state` only; the advancing work is done by `apply_decision`.
- `observe(state, agent_id) -> Observation` — structured, hidden-info-safe per-agent view.
- `apply_decision(state, action) -> list[EngineEvent]` — applies the chosen action, then runs
  all **mandatory** steps until the next genuine choice, storing it on the state.

An agent is anything implementing `choose(observation, options) -> action`. The deterministic
V1 policies (`engine/target_policy.py`, always-intercept, gains→self, build-launch
placement, weakest-target) **move into the baseline `HeuristicAgent`** as its decision logic;
the engine decides nothing strategic.

One unified driver loop powers `run_simulation`, the PettingZoo env, and the Concordia harness:

```python
advance_to_first_decision(state)
while (d := pending_decision(state)) is not None:
    obs = observe(state, d.agent_id)
    action = agents[d.agent_id].choose(obs, d.options)
    apply_decision(state, action)
```

## 3. The Decision type

```python
class DecisionType(StrEnum):
    PLACE = "place"                      # which hand/deterrent card into the 2nd face-down slot (mandatory)
    MODIFY_DETERRENT = "modify_deterrent" # move card hand<->deterrent, or skip (optional)
    LAUNCH_TARGET = "launch_target"      # which enemy a ready launch hits (mandatory once armed)
    SECRET_TARGET = "secret_target"      # target for an offensive secret (mandatory per secret)
    PROPAGANDA_TARGET = "propaganda_target" # whom to steal from during peace (mandatory per card)
    FINAL_STRIKE_TARGET = "final_strike_target" # retaliation target(s) for an eliminated player
    INTERCEPT = "intercept"              # DEFENDER: play a matching anti-missile, or decline
    PEACE_VOTE = "peace_vote"            # postal only
    PASS = "pass"                        # degenerate only: no available move (skipped turn, etc.)

@dataclass(frozen=True)
class Decision:
    agent_id: str                 # who must decide (may be the defender, not the turn player)
    decision_type: DecisionType
    options: list[LegalAction]    # the reified legal choices (existing LegalAction type)
    context: dict                 # decision-specific facts (e.g. INTERCEPT: incoming yield, attacker, delivery label)
```

`options` always contains the legal moves for `decision_type`. Optional decisions
(MODIFY_DETERRENT, INTERCEPT) always include an explicit "skip"/"decline" option so an agent
must actively choose. `context` carries the information an agent needs that isn't already in its
observation (it is also a strict subset of the observation, never hidden info).

## 4. The turn as a sequence of decisions

Mandatory steps auto-advance; only the bracketed items below surface as decisions.

1. **Draw** (auto): draw to the hand target, parking secrets out of hand.
2. **Resolve secrets**: self-effect secrets (gains) auto-resolve; each offensive secret →
   **[SECRET_TARGET]** (one decision per secret, resolved in order; a chain that eliminates the
   drawer halts further secrets — already handled).
3. **Slide** (auto): first face-down → face-up; resolve the face-up card:
   - delivery → becomes the pending delivery (auto); warhead → arms the pending delivery or is
     discarded (auto, per the expiry rule); other non-propaganda → discard (auto);
   - propaganda during peace → **[PROPAGANDA_TARGET]**; during war → discard (auto).
4. **Modify deterrents**: **[MODIFY_DETERRENT]** (optional; includes skip). After PLACE, locked
   until next turn (rules step 2/3).
5. **Place** a card into the 2nd face-down slot: **[PLACE]** (mandatory; source = hand or deterrent).
6. **Attack**: if a launch is armed, **[LAUNCH_TARGET]** — the attack is *mandatory* once a
   warhead is loaded (rules: "then you must launch an attack"), so the choice is only *which*
   enemy, never whether to fire; resolution then auto-follows. For the chosen target,
   **[INTERCEPT]** (defender decides) before the spinner/damage. The INTERCEPT decision is
   **always** surfaced to the defender — even when they hold no eligible anti-missile — because the
   rules require a defender to "signify that they are not intercepting even if they have no
   anti-missile cards" (so observers cannot infer their hand). When they hold none, the only option
   is *decline*; the public outcome ("intercepted" / "declined") is identical either way. Multiple
   armed launches resolve in sequence, each with its own LAUNCH_TARGET + INTERCEPT.
7. **End turn** (auto): advance clockwise (or to the last interceptor), with the no-skip/no-dup
   rule already implemented in `turn_player_ids`.

**Eliminations & final strikes:** when a nuclear/secret kill drops a player to 0, that player
gets **[FINAL_STRIKE_TARGET]** decisions for their retaliation arsenal (chaining as today);
propaganda kills grant none. These interleave as decisions for the eliminated agent.

**The interception interrupt** is just the next decision the state implies: after a LAUNCH_TARGET
is chosen and the launch resolves, `apply_decision` advances to an INTERCEPT decision whose
`agent_id` is the defender; after they decide, flow returns to the attacker's remaining launches,
then their turn end. No special control-flow — the cursor simply points at the defender.

## 5. State model

`apply_decision` is the only mutator that advances the cursor; `pending_decision` is a pure read
of `state.pending`. We add an explicit, small phase cursor to `GameState` so the next decision is
computable without re-deriving it ad hoc:

```python
@dataclass
class DecisionCursor:
    turn_player: str            # clockwise anchor (whose turn)
    phase: TurnPhase            # DRAW/SECRETS/SLIDE/DETERRENTS/PLACE/ATTACK/FINAL_STRIKE/END
    pending: Decision | None    # the surfaced choice, or None mid-auto-advance
```

Existing per-player transient state (`pending_orders["launches"]`, parked `secrets`,
`pending_delivery`, `final_strike`, etc.) is retained; the cursor coordinates *which* of these
produces the next decision. A "pending attack awaiting interception" sub-state is added to carry
the attacker/target/launch across the INTERCEPT decision.

Mandatory-step engine (draw, slide, auto-resolve, end-turn) is internal to `apply_decision` and is
exactly the logic already in `table_turn.py` / `engine/*`, re-sequenced around explicit pauses.

## 6. Baseline agents

`choose(observation, options) -> action`. Policies move here from the engine:
- **HeuristicAgent:** build delivery→warhead launches (PLACE), target the weakest opponent
  (LAUNCH_TARGET), highest-pop opponent for offensive SECRET/PROPAGANDA targets, gains→self,
  eliminator-first for FINAL_STRIKE_TARGET, always-intercept when able (INTERCEPT), skip
  deterrents. **It must reproduce today's policies so baseline seed outcomes are preserved.**
- **RandomAgent:** uniform `choose` over `options`.
- **InteractiveAgent / future LMAgent:** out of scope here; plug in via the same `choose`.

## 7. Observations

`observe(state, agent_id) -> Observation`, a **typed dataclass** (chosen for type-safety over a
loose dict; the env can flatten it to a gym space at its boundary):
- **Public:** war/peace, per-player population totals, eliminations, turn number, deterrent cards
  (public), the current `Decision` (type + options + context), recent public event summary.
- **Private (this agent only):** own hand, own parked secrets, own launch track (face-down hidden
  from others, visible to self), own pending launches.
- **Hidden-info-safe:** never exposes another player's hand, face-down cards, or secrets.
  In particular, a defender's INTERCEPT options are visible only to that defender; other agents
  see only the public outcome ("intercepted" / "declined"), never whether the defender *could*
  have intercepted. Reuses/extends `observation.py`. Structured only; text rendering belongs to
  the Concordia harness.

## 8. Testing strategy

- **Scripted-decision tests:** drive the machine with a fixed `options`-index sequence; assert
  state/events. Deterministic, no agent needed — the cleanest way to test rules.
- **Characterization / no-regression:** the existing tests stay green; because the baseline
  HeuristicAgent reproduces the engine's old policies, seeded outcomes and replay logs are
  preserved (any intentional change is asserted explicitly).
- **Replay validation:** the 240-game CLI sweep still passes (same engine event stream).
- **Observation safety:** property test that `observe(state, A)` never contains B's hidden info.

## 9. Migration stages

The migration moves one group of decisions at a time so behavior changes stay isolated.
Test comments refer to these stage labels:

1. **A0 — scaffolding:** add `Decision`/`DecisionType`/`DecisionCursor`, `pending_decision`,
   `apply_decision` wrapping today's turn driver with NO behavior change; one driver loop.
2. **A1 — already-agent decisions:** route PLACE and LAUNCH_TARGET through the new model.
3. **A2 — secrets & propaganda:** SECRET_TARGET, PROPAGANDA_TARGET become decisions; move the
   target policy into HeuristicAgent.
4. **A3 — interception interrupt:** INTERCEPT becomes a defender decision; make attack resolution
   pausable around it.
5. **A4 — final strike:** FINAL_STRIKE_TARGET becomes decisions; chaining preserved.
6. **A5 — deterrents:** MODIFY_DETERRENT decision + place-from-deterrent.
7. **A6 — converge loops:** reimplement `run_simulation` and `env_table` on the state machine;
   retire the bespoke turn driver and the env's action-granular path (fixes its intercept bug).
8. **B1 — observations:** finalize the structured `Observation` contract + safety tests.

Postal mode rides along where shared (PEACE_VOTE as a decision) but full postal/expansion
decisions are deferred.

## 10. Resolved questions / risks

- **Attack timing (RESOLVED, per rules):** confirmed against the goblins rules mirror — once a
  warhead is loaded onto a delivery, "you must launch an attack"; the only decision is the target.
  There is no separate "declare war / whether to first-strike" decision (war is declared *by*
  choosing a target). The defender's INTERCEPT is a genuine choice, always offered (see §4/§7).
- **Observation type (RESOLVED):** typed dataclass, for type-safety (§7).
- **Scope of A6 (RESOLVED):** retiring the old loops is the riskiest step. The action/event
  *vocabulary* (`LegalAction`, `EngineEvent`) and replay schema are preserved, which contains
  the blast radius.
