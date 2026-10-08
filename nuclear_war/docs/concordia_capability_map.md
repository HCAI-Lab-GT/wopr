# Concordia Capability Map

Decision record for gdm-concordia 2.4.0 usage in WOPR (as of 2026-07-02).
Every upstream capability is either **used**, **deliberately excluded** with a
reason, or a **candidate** for a named future workstream. The point is that
gaps are choices, not oversights. Update this file when the pin moves or a
verdict changes. Enforcement: `tests/unit/test_concordia_prefab_parity.py`
pins the entity assembly; the prompt-content and entity-log tests pin what
reaches the model.

## Entity components (`concordia.components.agent`)

| Capability | Verdict | Why |
| --- | --- | --- |
| `instructions.Instructions` | Used | Role framing per seat (`native_entity.py`). |
| `observation.ObservationToMemory` | Used | Writes each scene into memory. |
| `observation.LastNObservations` | Used | Recency replay into the act prompt (history 10). |
| `memory.ListMemory` | Used | Deterministic, no embedder; recency-only retrieval. |
| `memory.AssociativeMemory` + `AssociativeMemoryBank` | Excluded | Requires a sentence embedder; only associative retrieval benefits, which nothing uses. Revisit if a retrieval-heavy agent design lands. |
| `concat_act_component.ConcatActComponent` | Used | Act component; `randomize_choices=False`, `prefix_entity_name=False` for determinism. |
| `constant.Constant` | Excluded | Identity already reaches prompts via scene JSON; a goal/persona constant is a candidate for experiment configs. |
| `plan.Plan` | Candidate | Multi-step planning before action selection; invokes the model per act (cost + determinism impact). Decide during LM-experiment design, not harness work. |
| `all_similar_memories.AllSimilarMemories` | Excluded | Needs associative retrieval (embedder) and extra model calls. |
| `question_of_recent_memories.*` | Candidate | Reflection-style components; same cost/determinism caveats as Plan. |
| `observation.ObservationsSinceLastPreAct` | Excluded | LastNObservations covers the need; one observation stream per decision. |
| `report_function.ReportFunction` | Excluded | For injecting host-computed state; WOPR injects state via the scene instead. |
| `scripted_act.*` / `no_op_context_processor` | Excluded | Scripted behavior is handled by WOPR-side scripted clients. |

## Entity prefabs (`concordia.prefabs.entity`)

| Capability | Verdict | Why |
| --- | --- | --- |
| `minimal.Entity` | Used as reference | Our assembly mirrors it (parity-tested); not called directly because its `build()` requires an `AssociativeMemoryBank` (embedder). |
| `basic`, `basic_with_plan`, `rational`, `conversational` | Excluded | Heavier reasoning pipelines with extra model calls; revisit alongside Plan verdict. |
| `puppet`, `basic_scripted`, `fake_assistant_*` | Excluded | Scripted/puppet control lives in WOPR clients and configs. |

## Game master, simulation, environment

| Capability | Verdict | Why |
| --- | --- | --- |
| `prefabs.game_master.*` (dialogic, situated, marketplace, psychology_experiment, …) | Excluded by design | WOPR is the rules engine: legal actions, randomization, state mutation, and outcomes are engine-owned (2026-06-22 design spec). A Concordia GM would duplicate or fight the engine. |
| `prefabs.simulation.*` | Excluded by design | WOPR's harness (`run_concordia_no_press_game`) owns the loop, artifacts, and determinism guarantees. |
| Formative-memories initializer | Candidate | Seat backstories for press/faction experiments; trace/determinism impact must be assessed first. |

## Language model layer (`concordia.language_model`)

| Capability | Verdict | Why |
| --- | --- | --- |
| `LanguageModel` interface (`sample_text`/`sample_choice`) | Used | Implemented by `ConcordiaHTTPChoiceModel` with the blind-agent guard and letter mapping. |
| `no_language_model.NoLanguageModel` | Used | Deterministic first-legal seats (choice 0). |
| `RandomChoice` / `BiasedMedianChoice` models | Excluded | WOPR baselines (`RandomAgent`, heuristics) cover this with engine-side seeding. |
| Bundled provider model wrappers | Excluded | WOPR's `LLMHttpClient` owns provider access, retries, and usage metadata for trace parity with non-native seats. |

## Runtime and observability

| Capability | Verdict | Why |
| --- | --- | --- |
| `EntityAgentWithLogging.get_last_log()` | Used | Captured per decision into `rendered_observation.concordia.entity_log` (true model-visible prompt + per-component contributions). |
| `get_all_logs()` / `measurements` channels | Excluded | Per-decision capture at act time is sufficient; full-channel streaming would duplicate the trace sidecar. |
| `InteractiveDocument` | Used indirectly | Drives choice prompting inside `ConcatActComponent`; its `(a)/(b)` letter protocol is what `sample_choice` guards and maps. |
| Entity `get_state()`/`set_state()` checkpointing | Excluded | WOPR replays are the source of truth; entity state is rebuilt per run for determinism. |

## Press-mode verdicts (review, 2026-07-03)

Reviewed against the 2026-06-23 press-light and 2026-06-24 multi-turn public
press specs. The press layer stays WOPR-owned: scenes, clients, visibility
filtering, and trace parity live in `nuclear_war_concordia`, and HTTP remains
the press message producer (native seats are rejected when press is enabled).

| Capability | Verdict | Why |
| --- | --- | --- |
| `conversational` prefab / GM-mediated press dialogue | Excluded by design | Same rationale as the game-master row. A Concordia-driven dialogue loop would take ownership of turn order, message resolution, and memory injection away from the deterministic WOPR-side coordinator, breaking same-seed determinism, per-message trace auditability, and version-pin independence. Press stays a WOPR-side pass over `observe()`-derived scenes. |
| Entity-side `Constant` personas | Candidate (per-seat, behind the client seam) | A goal/persona constant enriches a seat's framing without touching the coordinator; adoptable per-seat through the client seam. Must state model-call cost and same-seed determinism impact before landing. |
| Formative-memories initializer | Candidate (per-seat, behind the client seam) | Seat backstories for press/faction experiments; per-seat, behind the client seam. Same cost/determinism gate. |
| `Plan` / reflection components | Candidate (per-seat, behind the client seam) | Multi-step planning or reflection before a press or action choice; invokes the model per act (cost + determinism impact), so gated on the same review. Per-seat, behind the client seam. |

The entity-side candidates are scoped to the per-seat client seam so they can
never perturb the coordinator's deterministic pass or the WOPR replay.
