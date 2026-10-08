"""CLI entry point that delegates to src/nuclear_war_env."""

from nuclear_war_env.main import main as phase0_main


def main() -> None:
    """Run the Phase 0 setup routine."""
    phase0_main()


if __name__ == "__main__":
    main()
