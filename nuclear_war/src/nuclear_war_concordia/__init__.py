"""Concordia adapter utilities for WOPR Nuclear War runs."""

from .runtime import detect_concordia_runtime
from .types import ConcordiaRuntimeStatus

__all__ = ["ConcordiaRuntimeStatus", "detect_concordia_runtime"]
