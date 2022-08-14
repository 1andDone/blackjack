# blackjack

Fully-customizable blackjack simulation.

![Blackjack](/documentation/blackjack.jpg?raw=true)

## Setup

Clone the repository and install locally via pip.

```python
pip install .
```

## Usage

Begin by setting up the `Blackjack` class object with certain house rules.

```python
from blackjack import Blackjack

blackjack = Blackjack(
    min_bet=10,
    max_bet=500,
    s17=True,
    blackjack_payout=1.5,
    max_hands=4,
    double_down=True,
    split_unlike_tens=False,
    double_after_split=False,
    resplit_aces=False,
    insurance=True,
    late_surrender=True,
    dealer_shows_hole_card=False
)
```

Next, create each player that will be added to the table. There are several different
card counting systems (both balanced and unbalanced) available for each `CardCounter`
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
    insurance=10,
    partner=player2,
    entry_point=3,
    exit_point=0
)
```

Finally, add all players and simulate.

```python
blackjack.add_player(player=player1)
blackjack.add_player(player=player2)
blackjack.add_player(player=player3)
blackjack.simulate(penetration=0.75, number_of_shoes=1000, shoe_size=6, seed=1)
```

## Results

Summary statistics are available after each run by using the `stats` method.

```python
print(player3.stats)

>> Amount wagered: $369,950.00 
>> Hands lost: 1,975 
>> Hands played: 4,097 
>> Amount earned: $3,097.50 
>> Hands won: 1,746 
>> Hands pushed: 376 
>> Insurance amount wagered: $660.00 
>> Insurance amount earned: -$210.00 
>> Total amount earned: $2,887.50 
>> Total amount wagered: $370,610.00 
>> Element of Risk: 0.84% 
```

If desired, the statistics at each count can be accessed as well.

```python
player3.stats.stats
```