"""Single-speaker press flow for the press coordinator."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.observation import Observation

from .press_speaker_flow import run_speaker
from .press_visibility import visible_to
from .types import ConcordiaClient


class PressSpeaker:
    def __init__(
        self,
        *,
        clients: dict[str, ConcordiaClient],
        identities: dict[str, dict[str, str]],
        press_sink: list[dict[str, Any]],
        max_retries: int = 1,
        mode: str = "press_light",
    ) -> None:
        self.clients = clients
        self.identities = identities
        self.press_sink = press_sink
        self.max_retries = max_retries
        self.mode = mode

    def run_speaker(
        self,
        *,
        speaker: str,
        observation: Observation,
        living: list[str],
        round_no: int,
        pass_no: int,
        prior_messages: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return run_speaker(
            self,
            speaker=speaker,
            observation=observation,
            living=living,
            round_no=round_no,
            pass_no=pass_no,
            prior_messages=prior_messages,
        )

    def _view(
        self, speaker: str, prior_messages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        return visible_to(speaker, prior_messages)
