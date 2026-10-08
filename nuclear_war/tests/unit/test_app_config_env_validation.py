"""AppConfig environment validation tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.config import AppConfig


def test_app_config_rejects_malformed_env_seed(monkeypatch) -> None:
    monkeypatch.setenv("NUCLEAR_WAR_SEED", "1.0")

    with pytest.raises(ValueError, match="NUCLEAR_WAR_SEED must be an integer"):
        AppConfig.from_env()
