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
from blackjack.enums import CountingStrategy
from blackjack.player import Player

player1 = Player(
    name='Player 1',
    bankroll=1000000,
    min_bet=10
)

player2 = CardCounter(
    name='Player 2',
    bankroll=10000,
    min_bet=10,
    counting_strategy=CountingStrategy.HI_LO,
    bet_ramp={
        1: 15,
        2: 20,
        3: 40,
        4: 50,
        5: 70,
        6: 100,
        7: 150,
        8: 200
    },
    insurance=None
)

player3 = BackCounter(
    name='Player 3',
    bankroll=15000,
    min_bet=10,
    counting_strategy=CountingStrategy.OMEGA_II,
    bet_ramp={
        1: 15,
        2: 20,
        3: 50,
        4: 100,
        5: 150,
        6: 250,
        7: 400,
        8: 500
    },
    insurance=10,
    entry_point=5,
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
print(player3.stats.summary)
```

```
>> HANDS PLAYED: 238,545
>> HANDS WON: 102,706
>> HANDS LOST: 115,391
>> HANDS PUSHED: 20,448
>> AMOUNT EARNED: $764,635.00
>> AMOUNT WAGERED: $64,313,200.00
>> INSURANCE AMOUNT EARNED: -$148,000.00
>> INSURANCE AMOUNT WAGERED: $570,600.00
>> TOTAL AMOUNT EARNED: $616,635.00
>> TOTAL AMOUNT WAGERED: $64,883,800.00
>> ELEMENT OF RISK: 0.95%
```

If desired, the statistics at each count can be accessed as well.

```python
player3.stats.stats
```