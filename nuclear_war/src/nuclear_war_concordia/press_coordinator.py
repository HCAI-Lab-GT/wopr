"""Press coordinator for Concordia press rounds."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.observation import Observation

from .press_speaker import PressSpeaker
from .types import ConcordiaClient


class PressCoordinator:
    def __init__(
        self,
        *,
        speakers: list[str],
        clients: dict[str, ConcordiaClient],
        identities: dict[str, dict[str, str]],
        press_sink: list[dict[str, Any]],
        max_retries: int = 1,
        passes: int = 1,
        mode: str = "press_light",
    ) -> None:
        if passes < 1:
            raise ValueError("PressCoordinator passes must be at least 1")
        self.speakers = speakers
        self.passes = passes
        self.mode = mode
        self.speaker = PressSpeaker(
            clients=clients,
            identities=identities,
            press_sink=press_sink,
            max_retries=max_retries,
            mode=mode,
        )

    def run_round_press(
        self,
        *,
        observations: dict[str, Observation] | list[Observation],
        round_no: int,
    ) -> list[dict[str, Any]]:
        obs_by_speaker = _as_observation_map(observations)
        living = list(obs_by_speaker)
        transcript: list[dict[str, Any]] = []
        for pass_no in range(1, self.passes + 1):
            self._run_pass(
                obs_by_speaker=obs_by_speaker,
                living=living,
                round_no=round_no,
                pass_no=pass_no,
                transcript=transcript,
            )
        return transcript

    def _run_pass(
        self,
        *,
        obs_by_speaker: dict[str, Observation],
        living: list[str],
        round_no: int,
        pass_no: int,
        transcript: list[dict[str, Any]],
    ) -> None:
        for speaker in self.speakers:
            if speaker not in obs_by_speaker:
                continue
            entry = self.speaker.run_speaker(
                speaker=speaker,
                observation=obs_by_speaker[speaker],
                living=living,
                round_no=round_no,
                pass_no=pass_no,
                prior_messages=list(transcript),
            )
            transcript.append(entry)


def _as_observation_map(
    observations: dict[str, Observation] | list[Observation],
) -> dict[str, Observation]:
    if isinstance(observations, dict):
        return dict(observations)
    return {obs.player_id: obs for obs in observations}
