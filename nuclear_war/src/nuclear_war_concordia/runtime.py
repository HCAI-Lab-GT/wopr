"""Runtime detection for optional Concordia integration."""

from __future__ import annotations

from .types import ConcordiaRuntimeStatus


def detect_concordia_runtime() -> ConcordiaRuntimeStatus:
    try:
        concordia = __import__("concordia")
    except ImportError as exc:
        return ConcordiaRuntimeStatus(
            runtime_path="concordia_style_fallback",
            available=False,
            detail=str(exc),
        )
    return ConcordiaRuntimeStatus(
        runtime_path="concordia_runtime",
        available=True,
        detail="imported concordia",
        version=getattr(concordia, "__version__", None),
    )
