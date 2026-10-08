# WOPR

WOPR is a social-simulation environment for studying how organizations make
high-stakes decisions. It is built on a deterministic, replay-validated rules
engine and uses wargames as the vehicle. The first instantiation is the
published card game *Nuclear War*.

On top of the engine, WOPR provides:

- a decision-point contract that turns every strategic choice into an explicit
  agent decision;
- language model agents, driven directly or through
  [Concordia](https://github.com/google-deepmind/concordia);
- a four-rung press ladder from no communication to private single-recipient
  channels with structured commitments;
- factions modeled as collective command-and-control systems (sole authority,
  council, distributed, automated) rather than single agents;
- a browser workbench for inspecting replays, decision traces, and press.

This repository accompanies the paper
[*No One Wins in Nuclear War: A Social Simulation of Military Decision-making*](https://arxiv.org/abs/2608.01868)
(Social Sim'26 Workshop at COLM 2026).

## Repository layout

- [`nuclear_war/`](nuclear_war/README.md): the Python package. Rules engine,
  PettingZoo environments, CLI, baseline and language model agents, the
  Concordia harness and press ladder, faction C2, example configs, and tests.
- [`wopr_visualizer/`](wopr_visualizer/README.md): a React replay workbench
  that loads replay JSON, decision-trace sidecars, press artifacts, and batch
  summaries, plus a Live view backed by a local engine process.

## Quick start

Requires Python 3.13 and [`uv`](https://docs.astral.sh/uv/).

```bash
cd nuclear_war
uv sync --extra dev
uv run nuclear-war validate-rules
uv run nuclear-war simulate --mode table --players 3 --seed 42 --agent heuristic --max-turns 100 --out /tmp/sim.json
uv run nuclear-war concordia-demo --config docs/examples/concordia_full_press_style_demo.json --out-dir /tmp/press
```

The last command runs a full-press game with offline seats, so no model
provider is needed. See [`nuclear_war/README.md`](nuclear_war/README.md) for
provider-backed runs, faction C2 batches, and the test gate.

To inspect the output:

```bash
cd wopr_visualizer
npm install
npm run dev
```

## Game data

*Nuclear War* is a card game designed by Douglas Malewicki. This project is not
affiliated with or endorsed by the game's designer or publishers. The
repository does not include the rulebook or exact card text. Card data is
limited to names, counts, and paraphrased effect summaries with confidence
labels; see
[`nuclear_war/docs/source_research_policy.md`](nuclear_war/docs/source_research_policy.md).

## Citation

```bibtex
@inproceedings{matlin2026nuclearwar,
  title         = {No One Wins in Nuclear War: A Social Simulation of Military Decision-making},
  author        = {Matlin, Glenn and Song, Isaac and Zang, Anthony Wen-Ming and Riedl, Mark},
  booktitle     = {Social Sim'26 Workshop at COLM 2026},
  year          = {2026},
  eprint        = {2608.01868},
  archivePrefix = {arXiv},
}
```
