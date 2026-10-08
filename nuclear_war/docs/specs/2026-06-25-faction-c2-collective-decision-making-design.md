# Faction C2: Collective Decision-Making for Nuclear War Factions

Design spec for adding per-faction collective command-and-control decision
systems.

Date: 2026-06-25

## Scope decisions

| Axis | Decision |
|---|---|
| Faction structure | Four structurally distinct C2 systems |
| C2 grounding | Literature-grounded archetypes; real systems cited as origin, not claimed as fidelity |
| Demonstration | Build all four archetypes; demonstrate one (Green/council) end to end |
| Anchoring | Factions remain fictional colors; real systems cited as archetype origins |

## Motivation

The base harness treats each of the four factions (blue, red, green, purple) as
a single agent under one persona. Real use-of-force decisions are made by groups
and institutional systems, not single actors. This addition reframes each faction
as a small command-and-control (C2) system that aggregates subordinate opinions
into a single release decision, grounded in the nuclear-use C2 literature.

The enabling technical fact: the existing decision-point contract already treats
any agent uniformly. A faction C2 system is an agent whose `choose` internally
runs a deliberation process and returns one action. No engine change.

## Positioning and claims

### Claims (calibrated to scope)

- C1 (strong, defensible). The decision-point contract admits collective
  decision-making systems as players with no engine change, because a faction is
  an agent that returns one action from `choose`. Verified by building four.
- C2 (strong, defensible). Four archetypes (sole-authority, consultative
  council, pre-delegated, automated-retaliation) are structurally distinct in
  where release authority aggregates, grounded in the nuclear-use C2 literature.
- C3 (demonstrated, narrow). One archetype (Green/council) is shown end to end
  as a worked decision trace: advisor opinions, aggregation, executive action,
  linked to engine replay. This demonstrates the mechanism, not a study.

### Non-claims

- No claim that the simulation models specific states.
- No claim that outcomes match real-world behavior.
- No claim that the structures are fiducial models of named systems.

## The four C2 structures

All four are agents returning one action from `choose(observation, options)`.
They differ on one literature-supported axis: where release authority
aggregates, and whether in-the-moment deliberation occurs.

| Archetype | Deliberation at release? | Aggregation rule | Real-system origin (cited, not fidelity) |
|---|---|---|---|
| A. Sole-authority | Yes, by one actor | None; advisors consulted, cannot bind | US NCA sole presidential authority (CRS IF10521); DPRK "button-on-desk" automaticity (NDU WMD Center) |
| B. Consultative council | Yes, by a required body | Conjunctive: members vote to one decision, all bound | Pakistan NCA + SPD three-tier (NTI, CFR, Sandia); NATO Nuclear Planning Group |
| C. Pre-delegated / distributed | No group deliberation; each holder checks a condition | Disjunctive: any authorized holder can release | PALs / NSAM-160 (Bellovin); pre-delegation (Lewis & Tertrais 2019) |
| D. Automated retaliation | No deliberation at release; policy set in advance | None at release; pre-set condition to action rule | Soviet Perimeter / "Dead Hand" (Blair; Hoffman, *The Dead Hand*) |

### Structural distinctions

- A vs B. A concentrates authority in one decider who may ignore advice; B
  requires the body to concur and the executive cannot override. Difference:
  advisory vs binding aggregation.
- B vs C. B synthesizes opinions into one shared decision (conjunctive); C has
  no synthesis, each holder independently authorizes and any one suffices
  (disjunctive). B is a committee; C is distributed launch authority.
- A/B/C vs D. A, B, C deliberate at release. D removes that deliberation; the
  decision was made once when the policy was armed. A human arms "combat mode"
  (Perimeter is not fully autonomous), but the system fires on a pre-set
  trigger, not fresh deliberation.

### Proposed faction mapping (configuration, not canonical)

| Faction | Archetype | Characterization |
|---|---|---|
| Blue | A, Sole-authority | An executive with a staff it may ignore |
| Green | B, Consultative council | A body that must concur; executive chairs |
| Purple | C, Pre-delegated / distributed | Multiple holders, any of whom can release |
| Red | D, Automated retaliation | A pre-armed policy that fires on trigger |

Mapping spreads the four across the authority-concentration axis so no two are
neighbors. Mapping is arbitrary and reassignable; it gives concrete names to
refer to.

## Configurability as the personality dimension

Each archetype exposes a different knob. The structure determines what is
configurable, which reframes "personality" from a single persona string toward
structural parameters.

- A (sole-authority). Advisor count, advisor personas, a `deference` parameter
  (0 ignores staff, 1 defers). Personality is the executive plus weight on
  staff.
- B (council). Council size, per-member weights, voting threshold (majority or
  supermajority), member personas. Personality is the composition and voting
  rule.
- C (distributed). Number of holders, each holder's release criterion (its
  envelope), whether a single holder or a quorum suffices. Personality is the
  distribution and per-holder thresholds.
- D (automated). The pre-set condition to action policy, the trigger threshold,
  the arming decision. Personality is set once, at policy time.

## Implementation shape

Composition only. No engine touch. Reuses the existing `DecisionAgent` protocol
and the existing `LLMDecisionAgent` / `llm_http` seats as subordinates.

### Files

- `src/nuclear_war_agents/faction_agent.py`. A composite `DecisionAgent`
  factory. Takes an archetype spec and subordinate-agent configs; returns one
  agent whose `choose` runs the archetype's aggregation.
- Four aggregation functions, one per archetype. Each small and single-purpose:
  sole-authority deference, council weighted vote with threshold, distributed
  any-holder/quorum release, automated policy-rule evaluation.
- Harness seating. A new seat kind `faction_c2`, nameable in the batch runner
  and `llm-experiment` config alongside `llm_http`, `heuristic`,
  `llm_first_legal`. The seat builds a faction agent from a config block.
- Deliberation recording. Each subordinate's opinion plus the aggregation
  result is kept on the faction agent as `last_deliberation`, outside the
  decision-trace sidecar, so the trace schema and same-seed determinism are
  unchanged. Concordia runs write these records to a separate C2 sidecar
  (`nuclear_war_concordia/c2_artifacts.py`), so a faction decision is
  inspectable as advisor to aggregation to action.

### Parity and replay

- A faction is an agent returning one `LegalAction`. The engine sees one action
  per decision, same as `heuristic`.
- For any fixed faction configuration, the aggregation is deterministic in its
  inputs. A seeded game with a faction seat produces a replay byte-identical to
  a single-agent seat that happened to return the same action. The 240-game
  parity invariant is unaffected because it is defined on the engine, not on
  agent internals.
- Trace and C2 artifacts are sidecars, separate from replay JSON. Faction
  deliberation never enters the replay.

Net: the engine's verified-rules and replay-validation guarantees are untouched.
The addition lives entirely above the contract, as press and the Concordia
harness do.

## Demonstration (build all four, demo one)

One worked decision trace for Green (council). Council aggregation is the most
visible: multiple named members vote with stated rationales, the vote
aggregates, the executive is bound by the threshold.

Demo artifact is a trace from one real game step: the observation the council
saw, each member's opinion and rationale, the weighted vote, the threshold
outcome, the resulting action, and the engine replay line that action produced.
No multi-game comparison, no behavioral claim. Keeps the "environment not
study" framing intact while demonstrating the mechanism end to end.

The other three archetypes are built and configurable but not traced in the
demonstration.

## Literature anchors

- Lewis, J. G. and Tertrais, B. (2019). *The Finger on the Button: The Authority
  to Use Nuclear Weapons in Nuclear-Armed States*. CNS Occasional Paper 45.
  Comparative typology of sole vs delegated authority across nuclear-armed
  states.
- NDU WMD Center. *North Korean Nuclear Command and Control: Alternatives and
  Implications*. Four NC2 models: automaticity, devolution, delegation,
  pre-delegation.
- Hoffman, D. E. (2009). *The Dead Hand: The Untold Story of the Cold War Arms
  Race and Its Dangerous Legacy*. Soviet Perimeter / "Dead Hand" semi-automated
  retaliation.
- Blair, B. G. Western technical reporting on Perimeter.
- CRS IF10521. *Authority to Launch Nuclear Forces*. US sole presidential
  authority.
- NTI, CFR, Sandia. Pakistan NCA + SPD three-tier command structure.

All cited as archetype origins and motivation, not as fidelity targets.

## Out of scope

- Empirical comparison across archetypes or personality parameter settings
  (future work).
- Fidelity modeling of any named real-world C2 system.
- Changes to the engine, the replay schema, or the existing parity invariant.
