"""CLI source-evidence target export tests."""

from __future__ import annotations

import json

from nuclear_war_env.cli import main


def test_cli_source_evidence_targets_outputs_public_safe_targets(capsys) -> None:
    code = main(["source-evidence-targets"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert code == 0
    assert payload["card_effect_target_count"] == 30
    assert payload["expansion_composition_target_count"] == 10
    assert payload["card_effect_targets"][0] == {
        "card_id": "nw_base_f135174f",
        "card_name": "Warhead 10 Mt",
        "card_type": "warhead",
        "count": 19,
    }
    assert payload["expansion_composition_targets"][0] == {
        "registry_id": "nw_postal_atomic_cannon",
        "postal_effect": "atomic_cannon",
        "supported_modes": ["postal"],
    }
    assert "private/" not in captured.out
