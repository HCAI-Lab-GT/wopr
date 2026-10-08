"""Stress-like repetition to ensure stubs remain deterministic."""

from nuclear_war_env.factory import create_phase0_aec_env, create_phase0_parallel_env


def test_aec_repeated_cycles() -> None:
    env = create_phase0_aec_env(max_cycles=3)
    env.reset()
    steps = 0
    for agent in env.agent_iter():
        is_done = env.terminations.get(agent, False) or env.truncations.get(
            agent, False
        )
        env.step((steps % 2) if not is_done else None)
        steps += 1
    assert steps >= 6


def test_parallel_repeated_cycles() -> None:
    env = create_phase0_parallel_env(max_cycles=3)
    observations, _ = env.reset()
    for _ in range(3):
        actions = {agent: 1 for agent in observations}
        observations, rewards, terminations, truncations, infos = env.step(actions)
        if not observations:
            break
    assert truncations == {"player_0": True, "player_1": True}
