"""SiliSocs-compatible backend entrypoint for WOPR demo runs."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from nuclear_war_env.llm_harness_batch import load_no_press_llm_batch_config

from .demo import run_silisocs_no_press_demo

if TYPE_CHECKING:

    class BackendApp:
        """Type-checking base for optional SiliSocs integration."""

    def app_action(method: Any = None, **kwargs: Any) -> Any: ...

else:
    try:
        from silisocs.environments.backends.base import BackendApp, app_action
    except ImportError:

        class BackendApp:
            """Fallback base when SiliSocs is not installed."""

        def app_action(method: Any = None, **kwargs: Any) -> Any:
            del kwargs

            def decorate(fn: Any) -> Any:
                return fn

            return decorate(method) if method is not None else decorate


@dataclass
class NuclearWarNoPressBackend(BackendApp):
    config_payload: Mapping[str, Any] | None = None
    config_path: str | None = None
    output_dir: str = "wopr_silisocs_demo"
    scenario_name: str = "nuclear_war_no_press"
    _agent_names: list[str] = field(default_factory=list, init=False)

    def initialize(self, agent_names: Sequence[str], **kwargs: Any) -> None:
        del kwargs
        self._agent_names = [str(agent_name) for agent_name in agent_names]

    def observe(self, actor_name: str, **kwargs: Any) -> str:
        del kwargs
        return (
            "Nuclear War no-press demo backend. "
            f"{actor_name} can trigger one WOPR run for {self.scenario_name}."
        )

    @app_action(
        selectable_name="run_demo",
        description="Run one WOPR Nuclear War no-press demo and write artifacts.",
    )
    def run_demo(self, agent_name: str) -> str:
        del agent_name
        result = run_silisocs_no_press_demo(
            load_no_press_llm_batch_config(self._payload()),
            Path(self.output_dir),
            scenario_name=self.scenario_name,
        )
        replay = Path(result["replay_path"]).relative_to(self.output_dir)
        traces = Path(result["trace_path"]).relative_to(self.output_dir)
        return f"Wrote {replay} and {traces}"

    def _payload(self) -> Mapping[str, Any]:
        if self.config_payload is not None:
            return dict(self.config_payload)
        if self.config_path is None:
            raise ValueError(
                "NuclearWarNoPressBackend requires config_payload or config_path"
            )
        return json.loads(Path(self.config_path).read_text(encoding="utf-8"))


__all__ = ["NuclearWarNoPressBackend"]
