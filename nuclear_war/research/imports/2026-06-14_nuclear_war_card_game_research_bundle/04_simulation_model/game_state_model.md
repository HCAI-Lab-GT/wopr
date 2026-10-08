# Game state model

## Entities

### Player

- `population_cards`: list of denominations held.
- `population_total_m`: integer millions.
- `hand`: private list of card IDs.
- `launch_track`: face-up, first face-down, second face-down.
- `deterrents`: public displayed cards still treated as part of hand.
- `active_delivery_systems`: delivery systems ready to carry warheads.
- `eliminated`: boolean.
- `pending_final_strike`: boolean.
- `skip_turns`: integer.
- `country_power`: optional expansion field.

### Card

- `name`
- `set`
- `type`
- `count`
- `effect_summary`
- `exact_text`
- `timing`
- `legality`
- `targeting`
- `source_ids`
- `verification_status`

### Game

- `war_state`: peace or war.
- `turn_order` and `current_player`.
- `draw_deck`, `discard`, `population_bank`.
- `variant`.
- `event_log`.
- `pending_press_messages`.
- `global_loss_triggered`.

## Population handling

Represent population as discrete cards, not just totals, because making change from the bank is a rule-visible operation. Store totals for convenience but treat card movement as authoritative.

## Hidden information

The simulator should separate:

- true state;
- public state;
- per-agent private state;
- inferred probabilities.

## Source confidence

Every rule or card effect should have a source link and confidence level. Exact card effects should remain `needs_verification` until transcribed from physical copy or official source.
