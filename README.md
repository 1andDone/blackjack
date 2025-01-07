# blackjack

A fully customizable blackjack simulation and training tool.

![Blackjack](/images/blackjack.jpg?raw=true)

## Overview

This package provides a flexible environment for simulating and training various Blackjack strategies, including card counting and back-counting techniques. Whether you want to practice basic strategy or experiment with advanced betting systems, this tool makes it easy to configure the game to your preferred rules and play style.

## Installation

Clone the repository and install locally via pip.

```python
pip install .
```

## Getting Started

### Setting up the Game

Create a `Blackjack` instance and configure the house rules to your liking.

```python
from blackjack.blackjack import Blackjack

blackjack = Blackjack(
    min_bet=10,
    max_bet=500,
    s17=True,
    blackjack_payout=1.5,
    max_hands=4,
    double_down=True,
    double_after_split=False,
    resplit_aces=False,
    insurance=True,
    late_surrender=True,
    dealer_shows_hole_card=False
)
```

### Creating Players

You can add different types of players to the game, each with unique behaviors and betting strategies.

#### Player

A `Player` uses basic strategy for every decision and always bets a fixed amount.

```python
from blackjack.player import Player

player = Player(
    name='Player',
    bankroll=1000000,
    min_bet=10
)
```

#### Card Counter

A `CardCounter` uses basic strategy in conjunction with a chosen card counting system. Bets vary based on the current running/true count.

```python
from blackjack.card_counter import CardCounter
from blackjack.enums import CardCountingSystem

card_counter = CardCounter(
    name='Card Counter',
    bankroll=50000,
    min_bet=10,
    card_counting_system=CardCountingSystem.HI_LO,
    bet_ramp={
        1: 10,
        2: 20,
        3: 40,
        4: 80,
        5: 150
    },
    insurance=None,
    training=True
)
```

#### Back Counter

A `BackCounter` is similar to a `CardCounter`, but they may join the table when the running/true count is favorable or leave it when it becomes unfavorable.

```python
from blackjack.back_counter import BackCounter
from blackjack.enums import CardCountingSystem

back_counter = BackCounter(
    name='Back Counter',
    bankroll=15000,
    min_bet=10,
    card_counting_system=CardCountingSystem.HI_LO,
    bet_ramp={
        1: 10,
        2: 20,
        3: 40,
        4: 80,
        5: 150
    },
    insurance=3,
    entry_point=2,
    exit_point=1,
    training=False
)
```

### Adding Players to the Table

Player's are dealt cards in the order that they are added.

```python
blackjack.add_player(player=player)
blackjack.add_player(player=card_counter)
blackjack.add_player(player=back_counter)
```

### Modes

#### Simulation Mode

Simulate a large number of shoes:

```python
blackjack.simulate(penetration=0.75, number_of_shoes=50000, shoe_size=8, seed=1)
```

#### Training Mode

Play individual rounds for practice:

```python
blackjack.training(penetration=0.65, shoe_size=6, seed=3)
```

> **_NOTE_:** To enable training mode, one `CardCounter` or `BackCounter` instance is required to have `training=True`.

### Viewing Results

After running either mode, each player’s performance can be reviewed:

```python
print(back_counter.stats.summary(string=True))
```

Example summary:

```
TOTAL ROUNDS PLAYED: 267,773
TOTAL HANDS PLAYED: 274,062
PLAYER HANDS WON: 117,821
PLAYER HANDS LOST: 132,534
PLAYER HANDS PUSHED: 23,707
PLAYER BLACKJACKS: 14,450
DEALER BLACKJACKS: 14,484
PLAYER DOUBLE DOWNS: 22,497
PLAYER SURRENDERS: 12,349
INSURANCE AMOUNT BET: $376,810.00
INSURANCE NET WINNINGS: -$120,750.00
AMOUNT BET: $14,306,490.00
NET WINNINGS: $158,225.00
TOTAL AMOUNT BET: $14,683,300.00
TOTAL NET WINNINGS: $37,475.00
```

If desired, the statistics at each count can be accessed as well.

```python
back_counter.stats.stats
```