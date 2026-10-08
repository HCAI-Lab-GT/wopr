from __future__ import annotations

DEFAULT_HOST, DEFAULT_PORT = "127.0.0.1", 8765
MAX_BODY_BYTES = 4096
API_PATHS = frozenset(("/session", "/state", "/decision", "/step-agent", "/artifacts"))
VITE_ORIGINS = {
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:5173",
    "http://localhost:5174",
}
UNKNOWN = "Unknown endpoint."
INVALID_BODY_LENGTH = "Invalid body length."
INVALID_JSON_BODY = "Invalid JSON body."
BODY_REQUIRED = "JSON body is required."
BODY_TOO_LARGE = "Request body is too large."


class ApiRequestError(Exception):
    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code


def parse_body_length(header: str | None) -> int:
    if header is None:
        raise ApiRequestError(400, "invalid_body", INVALID_BODY_LENGTH)
    try:
        length = int(header)
    except ValueError as exc:
        raise ApiRequestError(400, "invalid_body", INVALID_BODY_LENGTH) from exc
    if length <= 0:
        msg = INVALID_BODY_LENGTH if length < 0 else BODY_REQUIRED
        raise ApiRequestError(400, "invalid_body", msg)
    if length > MAX_BODY_BYTES:
        raise ApiRequestError(400, "invalid_body", BODY_TOO_LARGE)
    return length


def matches_type(value: object, expected: type) -> bool:
    return type(value) is int if expected is int else isinstance(value, expected)
