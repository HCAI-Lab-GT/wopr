"""Replay helper tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.replay import write_replay


def test_write_replay_rejects_invalid_payload_before_file_creation(tmp_path) -> None:
    output = tmp_path / "nested" / "invalid.json"

    with pytest.raises(ValueError, match="Replay file missing required field: seed"):
        write_replay(output, {"mode": "table"})

    assert not output.exists()
    assert not output.parent.exists()
