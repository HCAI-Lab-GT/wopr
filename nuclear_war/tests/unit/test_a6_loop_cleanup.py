from __future__ import annotations

from pathlib import Path


def test_table_simulation_no_longer_references_legacy_table_turn() -> None:
    source = Path("src/nuclear_war_env/simulation.py").read_text()

    assert "play_table_turn" not in source
    assert 'if config.mode == "table" and player.alive' not in source
