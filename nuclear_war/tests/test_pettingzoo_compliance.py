"""Ensure real v1 environments satisfy PettingZoo API requirements."""

import warnings

from pettingzoo.test import api_test, parallel_api_test

from nuclear_war_env.factory import create_postal_env, create_table_env

# pettingzoo emits these as UserWarnings instead of failing; each one is a
# real API violation, so the compliance tests promote them to failures.
VIOLATION_FRAGMENTS = (
    "Live agent was not given",
    "was dead last turn",
    "No agents present",
)


def _assert_no_violation_warnings(caught: list[warnings.WarningMessage]) -> None:
    violations = [
        str(entry.message)
        for entry in caught
        if any(fragment in str(entry.message) for fragment in VIOLATION_FRAGMENTS)
    ]
    assert violations == []


def test_table_env_api_compliance_full_game() -> None:
    env = create_table_env(seed=1)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        api_test(env, num_cycles=200)
    _assert_no_violation_warnings(caught)


def test_postal_env_api_compliance_full_game() -> None:
    env = create_postal_env(seed=1, press=False)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        parallel_api_test(env, num_cycles=200)
    _assert_no_violation_warnings(caught)


def test_postal_env_api_compliance_three_players() -> None:
    env = create_postal_env(seed=1, press=False, players=3)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        parallel_api_test(env, num_cycles=200)
    _assert_no_violation_warnings(caught)


def test_v1_envs_expose_space_methods_without_warnings() -> None:
    table = create_table_env(seed=1)
    postal = create_postal_env(seed=1)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        table.action_space("player_0")
        table.observation_space("player_0")
        postal.action_space("player_0")
        postal.observation_space("player_0")

    assert caught == []
