"""Load ignored local `.env` files. Never load `.env.secret`."""

from __future__ import annotations

import os
from pathlib import Path

ENV_FILENAMES = (".env",)


def load_local_dotenv(search_from: Path | None = None) -> tuple[str, ...]:
    loaded: list[str] = []
    for directory in _search_dirs(search_from):
        path = directory / ".env"
        if not path.is_file():
            continue
        loaded.extend(_apply_env_file(path))
        break
    return tuple(loaded)


def _search_dirs(search_from: Path | None) -> tuple[Path, ...]:
    start = (search_from or Path.cwd()).resolve()
    dirs = [start, *start.parents]
    package_root = Path(__file__).resolve().parents[2]
    repo_root = package_root.parent
    extras = [package_root, repo_root]
    seen: list[Path] = []
    for directory in [*dirs, *extras]:
        if directory not in seen:
            seen.append(directory)
    return tuple(seen)


def _apply_env_file(path: Path) -> list[str]:
    applied: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        name, value = line.split("=", 1)
        name = name.strip()
        if not name or name in os.environ:
            continue
        os.environ[name] = _unquote(value.strip())
        applied.append(name)
    return applied


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


__all__ = ["ENV_FILENAMES", "load_local_dotenv"]
