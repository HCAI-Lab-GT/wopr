from __future__ import annotations

from nuclear_war_agents import HTTPResponse


class SequenceTransport:
    def __init__(self, responses: list[HTTPResponse]) -> None:
        self._responses = responses
        self.call_count = 0

    def __call__(
        self,
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout_seconds: int,
    ) -> HTTPResponse:
        del url, headers, body, timeout_seconds
        response = self._responses[min(self.call_count, len(self._responses) - 1)]
        self.call_count += 1
        return response


class Clock:
    def __init__(self, *values: int) -> None:
        self._values = list(values)

    def __call__(self) -> int:
        return self._values.pop(0)
