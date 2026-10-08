# Rules engine specification

## Design principle

Implement the rules as modules. Do not hardcode a single edition. *Nuclear War* has spinner-era, dice-chart, expansion, postal, and current *Nuclear Destruction* branches.

## Core loop pseudocode

```text
initialize_game(variant)
while not terminal:
    if variant.simultaneous_orders:
        collect_orders_from_all_live_players()
        resolve_pbm_order_cycle()
    else:
        p = current_player
        if p.skip_turns > 0: decrement skip; advance_turn; continue
        draw_to_hand_target_and_resolve_secrets(p)
        slide_launch_track(p)
        modify_deterrents(p)
        place_card_in_second_face_down_slot(p)
        resolve_face_up_card(p)
        handle_eliminations_and_final_strikes()
        update_peace_war_state()
        advance_turn_with_intercept_jump_if_any()
```

## Attack function

```text
attack(attacker, target, delivery_system, warhead):
    set war_state = WAR
    defense = ask_target_for_defense(target, delivery_system)
    if defense.success:
        discard_attack_cards_as_edition_requires()
        set_next_player_if_anti_missile(defender)
        return
    result = randomizer.roll()
    damage = apply_randomizer_to_warhead(result, warhead)
    if result.global_loss:
        eliminate_all_players(no_winner=True)
        return
    apply_population_loss(target, damage)
    discard_or_retain_delivery_system_by_type_and_payload()
    if target.population_total <= 0:
        queue_or_execute_final_strike(target)
```

## Final strike function

```text
final_strike(eliminated_player):
    if eliminated_by == PROPAGANDA: return none
    gather all eligible delivery systems and warheads from hand/mat/launch track
    build legal launch packages
    choose targets for each package
    resolve each attack sequentially
    if another player is eliminated, queue/immediately resolve their final strike depending edition/variant
    after all final strikes from this elimination chain, return to peace if game continues
```

## AI agent interface

Each agent should receive:

- public game state;
- its private hand and population cards;
- variant rules;
- public press if enabled;
- prior event log;
- hidden card probabilities from source deck model if exact deck known.

Each agent should output:

- deterrent changes;
- card placement;
- target choices;
- whether to intercept;
- final strike package choices;
- optional press statements.

## Determinism and audit

Every stochastic result must be logged with:

- randomizer type;
- raw roll/spinner result;
- pre-modification warhead damage;
- modifiers;
- final population loss;
- source rule table ID.
