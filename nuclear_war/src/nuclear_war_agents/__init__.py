"""Agents for deterministic Nuclear War experiments."""

from .baseline import HeuristicAgent, RandomAgent
from .faction_agent import (
    DirectMemberFactory,
    FactionDecisionAgent,
    ScriptedSubordinateFactory,
    SubordinateFactory,
)
from .faction_aggregation import (
    aggregate_automated,
    aggregate_council,
    aggregate_distributed,
    aggregate_sole_authority,
)
from .faction_types import FactionConfig, FactionDeliberation, SubordinateVote
from .interactive import InteractiveAgent
from .llm_agent import LLMDecisionAgent
from .llm_fake_clients import FirstLegalLLMClient
from .llm_http_client import HTTPClientConfig, LLMHttpClient, LLMHttpError
from .llm_http_providers import HTTPProviderDefaults, known_http_providers
from .llm_http_transport import HTTPResponse, LLMConfigError
from .llm_prompt import render_legal_options, render_llm_prompt
from .llm_response import parse_llm_response
from .llm_scripted_client import ScriptedLLMClient
from .llm_types import (
    LLMCompletion,
    LLMDecisionTrace,
    LLMModelClient,
    ParsedLLMDecision,
    TraceRecorder,
)
from .observation_heuristic import ObservationHeuristicAgent

__all__ = [
    "FactionConfig",
    "DirectMemberFactory",
    "FactionDecisionAgent",
    "FactionDeliberation",
    "HeuristicAgent",
    "FirstLegalLLMClient",
    "HTTPClientConfig",
    "HTTPProviderDefaults",
    "HTTPResponse",
    "InteractiveAgent",
    "LLMCompletion",
    "LLMConfigError",
    "LLMDecisionAgent",
    "LLMDecisionTrace",
    "LLMHttpClient",
    "LLMHttpError",
    "LLMModelClient",
    "ObservationHeuristicAgent",
    "ParsedLLMDecision",
    "RandomAgent",
    "ScriptedLLMClient",
    "ScriptedSubordinateFactory",
    "SubordinateFactory",
    "SubordinateVote",
    "TraceRecorder",
    "aggregate_automated",
    "aggregate_council",
    "aggregate_distributed",
    "aggregate_sole_authority",
    "known_http_providers",
    "parse_llm_response",
    "render_legal_options",
    "render_llm_prompt",
]
