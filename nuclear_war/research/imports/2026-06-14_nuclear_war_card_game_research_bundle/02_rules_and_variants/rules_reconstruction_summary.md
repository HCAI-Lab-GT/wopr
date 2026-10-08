# Rules reconstruction summary

This summary combines the base *Nuclear War* rules mirror, the older spinner-era scan, current official *Nuclear Destruction* rules, and postal/PBM variants.

## Core object

Players represent major powers. Population is the central resource and victory metric. Eliminate every other player's population through propaganda or nuclear attacks while retaining at least 1 million of your own population. If all remaining players are destroyed, nobody wins.

## Components by edition/source

### Older spinner-era scan

- 1 rules sheet.
- 1 spinner.
- 1 population deck, 40 cards total.
- 2 missile/warhead card decks, 100 cards total.
- 2 strategy mats.

### Later base rules mirror

- 20 population cards in 1M, 2M, 5M, 10M, and 25M denominations.
- 100 Nuclear War cards: warhead, delivery system, propaganda, anti-missile, secret, or top secret.
- Two ten-sided dice for attack/fallout resolution.
- Placemat slots: face-up card, first face-down card, second face-down card, two deterrents, population cards.

### Official current Nuclear Destruction

- Spinner board.
- Nuclear Escalation die.
- Rulebook.
- Six player mats.
- Population deck.
- Two Nuclear Destruction decks.
- Booster deck.
- Box.

## Setup

The older spinner scan and later base rules both use starting population-card counts by player count:

| Players | Population cards per player |
|---:|---:|
| 2 | 15 |
| 3 | 10 |
| 4 | 8 |
| 5 | 7 |
| 6 | 6 |

Remaining population cards form the bank. Nuclear War cards are shuffled and each player receives 9 cards. Players resolve all initial Secrets and Top Secrets before normal play, drawing replacements until they hold a secret-free 9-card hand. Each player then commits two cards face down to the launch/strategy track.

## Turn sequence - base tabletop model

1. Draw until required hand size is reached. In the later base rules mirror this is 10 cards including in-play placemat cards except the face-up slot; in current *Nuclear Destruction*, draw up to 9 cards.
2. Resolve any Secrets or Top Secrets drawn immediately, drawing replacements as needed.
3. Slide the launch track: first face-down card becomes face-up, second face-down card becomes first face-down.
4. Optionally modify deterrent cards.
5. Place one card face down into the second face-down slot.
6. Reveal/resolve the face-up card.
7. Proceed clockwise unless an anti-missile interception changes turn order.

## Card resolution

- **Propaganda**: During peace, steals population from another player. During war, discarded with no effect in the base rules. Some modern cards have special wartime propaganda effects.
- **Delivery system**: Placed active/face-up to deliver a future warhead. If the next relevant face-up card is an eligible warhead, an attack occurs; otherwise the delivery system is normally discarded.
- **Warhead**: Must be preceded by a compatible delivery system. If compatible, attack is mandatory.
- **Anti-missile**: Normally played from hand in response to an attack, not useful when scheduled as a launch-track card.
- **Secret/Top Secret**: Event-like immediate effects. Older/current handling varies, but draw-and-resolve with replacement is central.
- **Special**: Expansion/modern reactive or special-action cards; use card-specific timing.

## War and peace

The game begins in peace. War begins when a target is chosen for a nuclear attack, even if the attack is intercepted, malfunctions, or duds. Propaganda is ineffective while war persists. Peace returns only after at least one player has been eliminated and any final strikes are resolved.

## Attack resolution

1. Launching player identifies the target.
2. Target may respond with an appropriate anti-missile or other legal defense.
3. If an anti-missile stops the attack, discard the attacking delivery system and exposed warheads as specified by the edition. The intercepting player may become the next player.
4. If not stopped, resolve the spinner/dice/randomizer.
5. Apply warhead population loss modified by randomizer result.
6. Discard missile + warhead after one use. Bombers may continue through multiple turns until payload is exhausted, failed, or invalidated by the next card sequence.

## Final retaliation

If a player loses all population because of nuclear attack or certain Secret/Top Secret effects, they may perform final retaliation. They combine eligible delivery systems and warheads from their hand/track/mat, choose targets, and resolve all attacks. If final retaliation eliminates another player, the newly eliminated player also gets a final strike, creating possible chain eliminations. A player eliminated by propaganda receives no final strike.

## Victory

The final remaining player wins only if they retain at least 1 million population. If final strikes eliminate everyone, the game has no winner.

## Edition-sensitive fields

A simulator should expose these as variant settings rather than hardcoding one edition:

- Starting population deck size: 20-card vs 40-card population deck.
- Randomizer: physical spinner vs two ten-sided dice vs Nuclear Escalation die option.
- Hand draw target: 9 vs 10 depending source.
- Anti-missile turn-order jump.
- Whether bomber payload can persist and exactly how it fails.
- Whether expansion cards/countries/special powers are included.
- Whether public press/diplomacy is allowed.
