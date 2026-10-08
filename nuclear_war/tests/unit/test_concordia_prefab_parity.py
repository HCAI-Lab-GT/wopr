"""Parity guard: our native entity must track Concordia's minimal prefab.

The 2026-07-01 blind-agent bug was a semantically wrong but API-valid entity
assembly (zero context components). This test pins our `_entity()` pipeline to
`concordia.prefabs.entity.minimal` — DeepMind's own minimal correct entity —
so upstream architectural drift across version bumps fails loudly instead of
silently degrading prompts.

Documented deviations from the prefab (see `_context_components` in
`nuclear_war_concordia/native.py`):
- `ListMemory` instead of `AssociativeMemory`: only recency retrieval is used
  and `AssociativeMemoryBank` requires a sentence embedder. Both subclass the
  same `Memory` base, which is what this test enforces.
- `randomize_choices=False` and `prefix_entity_name=False` for deterministic
  option ordering.
- Shorter observation history (prompt-size control), not asserted here.
"""

from __future__ import annotations

from typing import Any, cast

import pytest


def test_native_entity_matches_minimal_prefab_pipeline() -> None:
    pytest.importorskip("concordia")
    import numpy as np
    from concordia.associative_memory.basic_associative_memory import (
        AssociativeMemoryBank,
    )
    from concordia.components.agent import memory as memory_component
    from concordia.language_model.no_language_model import NoLanguageModel
    from concordia.prefabs.entity import minimal

    from nuclear_war_concordia import native

    ours = cast(
        Any, native.build_native_first_legal_client({"name": "Commander 0"}).entity
    )
    prefab = minimal.Entity(
        params=cast(Any, {"name": "Commander 0", "randomize_choices": False})
    ).build(
        model=NoLanguageModel(),
        memory_bank=AssociativeMemoryBank(sentence_embedder=lambda _text: np.ones(3)),
    )

    ours_types = _ordered_component_types(ours)
    prefab_types = _ordered_component_types(prefab)

    assert len(ours_types) == len(prefab_types), (
        f"component pipeline diverged from the minimal prefab: "
        f"ours={[t.__name__ for t in ours_types]} "
        f"prefab={[t.__name__ for t in prefab_types]}"
    )
    for our_type, prefab_type in zip(ours_types, prefab_types, strict=True):
        if our_type is prefab_type:
            continue
        # The one allowed substitution: any Memory-base component may stand in
        # for the prefab's memory component.
        assert issubclass(our_type, memory_component.Memory), (
            f"unexpected component substitution: {our_type.__name__} "
            f"where the prefab has {prefab_type.__name__}"
        )
        assert issubclass(prefab_type, memory_component.Memory)


def test_native_act_component_keeps_determinism_contract() -> None:
    pytest.importorskip("concordia")

    from nuclear_war_concordia import native

    entity = cast(
        Any, native.build_native_first_legal_client({"name": "Commander 0"}).entity
    )
    act = entity.get_act_component()
    state = act.get_state()

    assert state["randomize_choices"] is False
    assert state["prefix_entity_name"] is False
    # Every context component must feed the act prompt, in insertion order.
    assert list(act.get_context_concat_order()) == list(
        entity.get_all_context_components().keys()
    )


def _ordered_component_types(agent) -> list[type]:
    components = agent.get_all_context_components()
    order = agent.get_act_component().get_context_concat_order() or components.keys()
    return [type(components[key]) for key in order]
