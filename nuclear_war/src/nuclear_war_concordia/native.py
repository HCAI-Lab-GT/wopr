"""Native Concordia entity/action-spec clients."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from nuclear_war_agents import HTTPClientConfig, LLMCompletion, LLMHttpClient

from .native_entity import (
    _choice_action_spec,
    _entity,
    _is_invalid_response_error,
    _no_language_model_module,
)
from .native_helpers import action_ids, entity_log, scene_payload
from .native_http_model import ConcordiaHTTPChoiceModel

ActionSpecFactory = Callable[..., Any]


class ConcordiaEntity(Protocol):
    def observe(self, observation: str) -> None: ...

    def act(self, action_spec: Any) -> str: ...


@dataclass
class NativeConcordiaEntityClient:
    entity: ConcordiaEntity
    identity: Mapping[str, str]
    model: ConcordiaHTTPChoiceModel | None = None
    action_spec_factory: ActionSpecFactory | None = None
    last_entity_log: dict[str, Any] | None = None

    def complete(self, scene_text: str) -> str | LLMCompletion:
        payload = scene_payload(scene_text)
        legal_ids = action_ids(payload)
        # Reset so a failed act never leaves a stale log attached to the
        # next decision's trace; only a successful act repopulates it.
        self.last_entity_log = None
        if self.model is not None:
            self.model.last_completion = None
        self.entity.observe(scene_text)
        action_spec = self._action_spec(legal_ids)
        try:
            choice = self.entity.act(action_spec)
        except Exception as exc:
            completion = self._last_completion()
            if _is_invalid_response_error(exc) and completion is not None:
                # Surface the raw model output so ConcordiaDecisionAgent can
                # apply its normal parse/validation retry path instead of
                # failing the run on the first malformed choice.
                return completion
            if completion is not None and not hasattr(exc, "completion"):
                exc.__dict__["completion"] = completion
            raise
        self.last_entity_log = entity_log(self.entity)
        raw_response = json.dumps(
            {"action_id": choice, "rationale": "native_concordia_choice"}
        )
        completion = self._last_completion()
        if completion is None:
            return raw_response
        return LLMCompletion(
            raw_response=raw_response,
            provider_latency_ms=completion.provider_latency_ms,
            provider_cost=completion.provider_cost,
            provider_usage=completion.provider_usage,
            provider_label=completion.provider_label,
            provider_model=completion.provider_model,
            provider_transport_retries=completion.provider_transport_retries,
        )

    def _action_spec(self, action_ids: tuple[str, ...]) -> Any:
        factory = self.action_spec_factory or _choice_action_spec
        return factory(
            call_to_action="Choose one legal WOPR action_id.",
            options=action_ids,
            tag="wopr_action",
        )

    def _last_completion(self) -> LLMCompletion | None:
        if self.model is None:
            return None
        return self.model.last_completion


def build_native_first_legal_client(
    identity: Mapping[str, str],
) -> NativeConcordiaEntityClient:
    model = _no_language_model_module().NoLanguageModel()
    return NativeConcordiaEntityClient(
        entity=_entity(identity, model),
        identity=identity,
    )


def build_native_http_client(
    identity: Mapping[str, str],
    config: HTTPClientConfig,
    *,
    request_guard: Callable[[], None] | None = None,
    input_token_guard: Callable[[str], None] | None = None,
) -> NativeConcordiaEntityClient:
    kwargs = {}
    if request_guard is not None:
        kwargs["request_guard"] = request_guard
        kwargs["input_token_guard"] = input_token_guard
    client = LLMHttpClient(config, **kwargs)
    model = ConcordiaHTTPChoiceModel(client)
    return NativeConcordiaEntityClient(
        entity=_entity(identity, model),
        identity=identity,
        model=model,
    )
