# blackjack

Fully-customizable blackjack simulation.

![Blackjack](/images/blackjack.jpg?raw=true)

## Setup

Clone the repository and install locally via pip.

```python
pip install .
```

## Usage

Begin by setting up the `Blackjack` class object with certain house rules.

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

Next, create each player that will be added to the table. There are several different
card counting systems (both balanced and unbalanced) available for each `CardCounter`
and `BackCounter` class instance. `Player` class instances do not count cards.


```python
from blackjack.back_counter import BackCounter
from blackjack.card_counter import CardCounter
from blackjack.enums import CardCountingSystem
from blackjack.player import Player

player1 = Player(
    name='Player 1',
    bankroll=1000000,
    min_bet=10
)

player2 = CardCounter(
    name='Player 2',
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
    insurance=None
)

player3 = BackCounter(
    name='Player 3',
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
    exit_point=1
)
```

Finally, add all players and simulate.

```python
blackjack.add_player(player=player1)
blackjack.add_player(player=player2)
blackjack.add_player(player=player3)
blackjack.simulate(penetration=0.75, number_of_shoes=50000, shoe_size=8, seed=1)
```

## Results

Summary statistics are available after each run by using each player's `stats` method.

```python
print(player3.stats.summary(string=True))
```

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
player3.stats.stats
```