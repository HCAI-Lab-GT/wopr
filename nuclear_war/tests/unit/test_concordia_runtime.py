"""Concordia runtime probe tests."""

from __future__ import annotations

import builtins

from nuclear_war_concordia.runtime import detect_concordia_runtime


def test_detect_concordia_runtime_reports_fallback_when_import_missing(
    monkeypatch,
) -> None:
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "concordia":
            raise ImportError("missing concordia")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    status = detect_concordia_runtime()

    assert status.runtime_path == "concordia_style_fallback"
    assert status.available is False
    assert "missing concordia" in status.detail


def test_detect_concordia_runtime_reports_runtime_when_import_succeeds(
    monkeypatch,
) -> None:
    real_import = builtins.__import__

    class FakeConcordia:
        __version__ = "test-version"

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "concordia":
            return FakeConcordia()
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    status = detect_concordia_runtime()

    assert status.runtime_path == "concordia_runtime"
    assert status.available is True
    assert status.version == "test-version"
