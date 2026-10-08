"""Integration smoke test for Phase 0 stub environments."""

from nuclear_war_env.factory import create_phase0_aec_env, create_phase0_parallel_env


def test_aec_roundtrip() -> None:
    env = create_phase0_aec_env(max_cycles=1)
    env.reset()
    for _agent in env.agent_iter():
        observation, reward, termination, truncation, info = env.last()
        assert isinstance(observation, dict)
        assert "observation" in observation
        assert "action_mask" in observation
        assert reward == 0
        assert info == {}
        action = 0 if not (termination or truncation) else None
        env.step(action)


def test_parallel_roundtrip() -> None:
    env = create_phase0_parallel_env(max_cycles=1)
    observations, infos = env.reset()
    assert set(observations) == {"player_0", "player_1"}
    actions = {agent: 0 for agent in observations}
    observations, rewards, terminations, truncations, infos = env.step(actions)
    assert rewards == {"player_0": 0.0, "player_1": 0.0}
    assert all(isinstance(truncations[agent], bool) for agent in truncations)
