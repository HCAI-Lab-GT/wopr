"""Native Concordia entity assembly and runtime-error classification."""

from __future__ import annotations

import importlib
from collections.abc import Mapping
from typing import Any

_INSTRUCTIONS_COMPONENT_KEY = "instructions"
_OBSERVATION_TO_MEMORY_COMPONENT_KEY = "observation_to_memory"
# Scenes are large JSON payloads; ten most-recent observations keeps prior
# decision context in the act prompt without unbounded prompt growth.
_OBSERVATION_HISTORY_LENGTH = 10

# Static, import-free descriptor of the native seat's context-component keys for
# the agent_metadata artifact. These are the exact keys ``_context_components``
# below registers the components under, so they match the entity_log channel
# names surfaced in the trace. The last two mirror Concordia's
# DEFAULT_OBSERVATION_COMPONENT_KEY / DEFAULT_MEMORY_COMPONENT_KEY ("__observation__"
# / "__memory__"); they are inlined as literals so the list can be reported even
# when the Concordia runtime is unavailable (fallback mode).
NATIVE_CONTEXT_COMPONENTS = (
    _INSTRUCTIONS_COMPONENT_KEY,
    _OBSERVATION_TO_MEMORY_COMPONENT_KEY,
    "__observation__",
    "__memory__",
)


def _entity(identity: Mapping[str, str], model: Any) -> Any:
    agent_module = importlib.import_module("concordia.agents.entity_agent_with_logging")
    act_module = importlib.import_module(
        "concordia.components.agent.concat_act_component"
    )
    agent_name = identity.get("name", "Concordia agent")
    context_components = _context_components(agent_name)
    act_component = act_module.ConcatActComponent(
        model=model,
        component_order=list(context_components.keys()),
        prefix_entity_name=False,
        randomize_choices=False,
    )
    return agent_module.EntityAgentWithLogging(
        agent_name=agent_name,
        act_component=act_component,
        context_components=context_components,
    )


def _context_components(agent_name: str) -> dict[str, Any]:
    """Concordia 2.4 prefab-style context pipeline for one WOPR seat.

    ObservationToMemory writes each observed scene into the memory component
    and LastNObservations replays the most recent scenes into the act prompt.
    ListMemory is used instead of AssociativeMemoryBank because only recency
    retrieval is needed and it stays deterministic without a sentence
    embedder, so NoLanguageModel first-legal seats keep same-seed replays.
    """
    instructions_module = importlib.import_module(
        "concordia.components.agent.instructions"
    )
    observation_module = importlib.import_module(
        "concordia.components.agent.observation"
    )
    memory_module = importlib.import_module("concordia.components.agent.memory")
    return {
        _INSTRUCTIONS_COMPONENT_KEY: instructions_module.Instructions(
            agent_name=agent_name
        ),
        _OBSERVATION_TO_MEMORY_COMPONENT_KEY: (
            observation_module.ObservationToMemory()
        ),
        observation_module.DEFAULT_OBSERVATION_COMPONENT_KEY: (
            observation_module.LastNObservations(
                history_length=_OBSERVATION_HISTORY_LENGTH
            )
        ),
        memory_module.DEFAULT_MEMORY_COMPONENT_KEY: memory_module.ListMemory(
            memory_bank=[]
        ),
    }


def _is_invalid_response_error(exc: Exception) -> bool:
    try:
        language_model = importlib.import_module(
            "concordia.language_model.language_model"
        )
    except ImportError:
        return False
    return isinstance(exc, language_model.InvalidResponseError)


def _no_language_model_module() -> Any:
    return importlib.import_module("concordia.language_model.no_language_model")


def _choice_action_spec(**kwargs: Any) -> Any:
    module = importlib.import_module("concordia.typing.entity")
    return module.choice_action_spec(**kwargs)
