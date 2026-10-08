"""Interactive agent that prompts the user for decisions."""

from __future__ import annotations

from dataclasses import dataclass

from nuclear_war_env.actions import LegalAction
from nuclear_war_env.rng import SeededRNG


@dataclass
class InteractiveAgent:
    rng: SeededRNG

    def choose(self, actions: list[LegalAction]) -> LegalAction:
        print("\n--- INTERACTIVE AGENT PROMPT ---")
        print(f"Player: {actions[0].player_id}")
        print("Available actions:")

        for i, action in enumerate(actions):
            payload_str = str(action.payload) if action.payload else ""
            print(f"  [{i}] {action.action_type.name} {payload_str}")

        while True:
            try:
                choice_str = input(f"Choose action [0-{len(actions) - 1}]: ")
                choice_idx = int(choice_str)
                if 0 <= choice_idx < len(actions):
                    print("--------------------------------\n")
                    return actions[choice_idx]
                print("Invalid index. Try again.")
            except ValueError:
                print("Invalid input. Enter a number.")
            except EOFError:
                # Fallback to random if script is non-interactive
                print("\nEOF encountered, falling back to random choice.")
                return self.rng.choose(actions)
