# blackjack

Fully-customizable blackjack simulation.

![Blackjack](/documentation/blackjack.jpg?raw=true)

## Setup

Clone the repository and install locally via pip.

```python
pip install .
```

## Usage

Begin by setting up the house rules.

```python
from blackjack import HouseRules

rules = HouseRules(
    shoe_size=6,
    min_bet=10,
    max_bet=500,
    s17=True,
    blackjack_payout=1.5,
    max_hands=4,
    double_down=True,
    split_unlike_tens=True,
    double_after_split=True,
    resplit_aces=False,
    insurance=True,
    late_surrender=True,
    dealer_shows_hole_card=False,
    dealer_shows_burn_card=False
)
```

Next, set up the table where each player will play.

```python
from blackjack import Table

table = Table(rules=rules)
```

Create each player and add them to the table. There are several different card
counting systems (both balanced and unbalanced) available for each `CardCounter`
and `BackCounter` class instance.


```python
from blackjack import Player, CardCounter, BackCounter
from blackjack import CountingStrategy

player1 = Player(
    name='Player 1',
    bankroll=1000,
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
        5: 70
    },
    insurance=None
)

player3 = BackCounter(
    name='Player 3',
    bankroll=10000,
    min_bet=10,
    counting_strategy=CountingStrategy.HI_LO,
    bet_ramp={
        1: 15,
        2: 20,
        3: 80,
        4: 120,
        5: 150
    },
    insurance=2,
    partner=player2,
    entry_point=3,
    exit_point=0
)

table.add_player(player=player1)
table.add_player(player=player2)
table.add_player(player=player3)
```

Finally, create the blackjack table and simulate.

```python
from blackjack import Blackjack

blackjack = Blackjack(
    rules=rules,
    table=table
)

blackjack.simulate(penetration=0.75, number_of_shoes=100, seed=1)
```

## Results

Summary statistics are available after each run by using the `stats` method.

```python
player3.stats
```

```
>> Amount wagered: $20,785.00 
>> Hands lost: 203 
>> Hands played: 411 
>> Amount earned: $312.50 
>> Hands won: 176 
>> Hands pushed: 32 
>> Element of Risk: 1.5% 
```

If desired, the statistics at each count can be accessed as well.

```python
player3.stats.stats
```