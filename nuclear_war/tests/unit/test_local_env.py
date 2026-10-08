"""Local .env loading. Never load .env.secret."""

from __future__ import annotations

import os
from pathlib import Path

from nuclear_war_env.local_env import ENV_FILENAMES, load_local_dotenv


def test_load_local_dotenv_reads_dotenv_not_secret(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    (tmp_path / ".env").write_text("TOGETHER_API_KEY=from-env\n", encoding="utf-8")
    (tmp_path / ".env.secret").write_text(
        "TOGETHER_API_KEY=from-secret\n", encoding="utf-8"
    )

    loaded = load_local_dotenv(search_from=tmp_path)

    assert loaded == ("TOGETHER_API_KEY",)
    assert os.environ["TOGETHER_API_KEY"] == "from-env"
    assert ENV_FILENAMES == (".env",)


def test_load_local_dotenv_does_not_override_existing(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setenv("TOGETHER_API_KEY", "already-set")
    (tmp_path / ".env").write_text("TOGETHER_API_KEY=from-env\n", encoding="utf-8")

    loaded = load_local_dotenv(search_from=tmp_path)

    assert loaded == ()
    assert os.environ["TOGETHER_API_KEY"] == "already-set"


def test_load_local_dotenv_skips_fifo(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.delenv("TOGETHER_API_KEY", raising=False)
    fifo = tmp_path / ".env"
    os.mkfifo(fifo)

    loaded = load_local_dotenv(search_from=tmp_path)

    assert loaded == ()
    assert "TOGETHER_API_KEY" not in os.environ
