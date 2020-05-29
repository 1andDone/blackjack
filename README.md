# blackjack

Blackjack simulation that allows the user to fully customize the house rules as well as multiple facets of an individual player's gameplay and strategy. The simulation plays through a user-specified number of shoes and produces default statistics and visualizations at the completion of each simulation.  

![Blackjack](/documentation/blackjack.jpg?raw=true)

## Setup House Rules

This simulation allows the user to fully customize the house rules. By default, these rules are configured for the *Vegas Strip* variant of blackjack which states that:

- Dealer stands on soft 17 `s17`
- Blackjack pays 3:2 `blackjack_payout`
- Players can split their hand 3 times, making up to 4 hands `max_hands`
- Players can double down on any two cards `double_down`
- Unlike 10-value cards may be split (i.e. 10-J) `split_unlike_tens`
- Players can double down after splitting `double_after_split`
- Aces can be split only once `resplit_aces`
- Players can only take one card to split Aces `default`
- Insurance on a dealer Ace pays 2-1 `insurance`
- Players are allowed to surrender after dealer checks for blackjack and forfeit half their original wager `late_surrender`
- 21 on a split Ace does not count as Blackjack `default`

Additional parameters allow the user to specify the following:

- Number of decks of cards that will be used in a shoe `shoe_size`
- Minimum and maximum bet allowed at the table `bet_limits`
- Dealer reveals hole card even when all players surrender, bust, or have a natural blackjack `dealer_shows_hole_card`
    - This setting will only have an impact on players that are counting cards. By default, `dealer_shows_hole_card=True`.

An example of the *Vegas Strip* configuration is seen below:
```python
r = HouseRules(
            shoe_size=6,
            bet_limits=[10, 500],
            s17=True,
            blackjack_payout=1.5,
            max_hands=4,
            double_down=True,
            split_unlike_tens=True,
            double_after_split=True,
            resplit_aces=False,
            insurance=True,
            late_surrender=True,
            dealer_shows_hole_card=True
)
```

## Setup Table

Betting, playing, and card counting strategies for individual players can also be customized in this simulation. Individual players have the following parameters:

- Name of the player `name`
- Amount of money the player begins with when sitting down at the table `bankroll`
- Minimum amount of money the player is willing to wager when playing a hand `min_bet`
- Ratio of the player's maximum bet to minimum bet `bet_spread`
- List of tuples indicating the running or true count as well as the amount of money wagered for running or true counts closest to, but not equaling or exceeding, that particular running or true count. These values are used to create a bet ramp with `len(bet_count_amount) + 1` partitions, each incremented by a defined amount `bet_count_amount`
    - For example, assuming `min_bet=10`, `bet_strategy='Spread'`, `bet_spread=3`, and `count_strategy='Hi-Lo'`, setting `bet_count_amount=[(1, 10), (4, 15)]` would create the following bet ramp:
    
        | Amount Bet | Hi-Lo True Count |
        |:----------:| :---------------:|
        | $10        | <1               |
        | $15        | 1 - <4           |
        | $30        | >=4              |
    
- Playing strategy used by the player `play_strategy`
    - Currently, all players adhere to *Basic* strategy for playing decisions. See [documentation](documentation/H17_S17_Basic_Strategy.xlsx) for more details.
- Betting strategy used by the player `bet_strategy`
    - Options include *Flat*, where the player bets the same amount each hand, and *Spread*, where the player bets according to their bet scale.
- Card counting strategy used by the player, if any `count_strategy`
    - Options include balanced counting systems (*Hi-Lo*, *Hi-Opt I*, *Hi-Opt II*, *Omega II*, *Halves*, *Zen Count*) as well as unbalanced counting systems (*KO*).
- Minimum true or running count at which the player will take the insurance bet, if available `insurance`
- Strategy in which a player counts cards at a table but does not play a hand `back_counting` 
- Running or true counts at which a back counter will start and stop playing hands at the table `back_counting_entry_exit`

An example table setup is seen below:
```python
p = [
        Player(
            name='Card Counter',
            rules=r,
            bankroll=12000,
            min_bet=10,
            bet_spread=10,
            bet_count_amount=[(1, 10), (3, 50), (7, 75)],
            play_strategy='Basic',
            bet_strategy='Spread',
            count_strategy='Halves',
            insurance=5
        ),
        Player(
            name='Average',
            rules=r,
            bankroll=750,
            min_bet=15,
            play_strategy='Basic',
            bet_strategy='Flat',
            count_strategy=None,
        ),
        Player(
            name='Back Counter',
            rules=r,
            bankroll=50000,
            min_bet=25,
            bet_spread=12,
            bet_count_amount=[(1, 25), (3, 95), (5, 165), (10, 235)],
            play_strategy='Basic',
            bet_strategy='Spread',
            count_strategy='Hi-Lo',
            back_counting=True,
            back_counting_entry_exit=[5, 1]
        )
]
```

## Setup Shoe Simulations

Now that the rules and table have been set, it's time to set up the shoe simulation. Below, a few important parameters are highlighted for the shoe simulation:

- Initializes the pseudorandom number generator to replicate the ordering of the shoe from run-to-run `seed_number`
- Number of shoes to simulate `simulations`
- Percentage of a shoe played before the shoe is re-shuffled `penetration`
- Option to create default visualizations for each player `figures`
    - See the [Figures](#figures) section for more information.

An example shoe simulation is seen below:
```python
ps = PlayShoe(
        rules=r,
        players=p,
        seed_number=78,
        simulations=10000,
        penetration=0.75,
        figures=True
)
```

## Run 

Finally, after setting everything up, the code below runs the shoe simulation:
```python
ps.main()
```

## Results

By default, basic shoe simulation statistics will be printed off. These include:

- *Rules* - rules used when running the simulation
- *Total rounds played* - number of rounds played by an individual player
- *Split hands* - number of additional hands played by an individual player after splitting
- *Total amount bet* - combination of the initial wager and additional wagers from splits and doubling made by an individual player
- *Total initial bet* - only includes the initial wagers made by an individual player (does not include additional wagers from splits and doubling)
- *Total net winnings* - total amount won less total amount lost by an individual player
- *House edge* - ratio of an individual player's total net winnings to total initial bet
- *Element of risk* - ratio of an individual player's total net winnings to total amount bet

```
Rules: 6 decks, S17, 1.5x BJ, DAS, LS
-------------------------------------


Player: Card Counter
--------------------
Total rounds played: 285193.0
Split hands: 7822.0
Total amount bet: 7437657.5
Total initial bet: 6590615.0
Total net winnings: 25702.5
House edge: 0.3899863669778921
Element of risk: 0.3455725139265958


Player: Average
---------------
Total rounds played: 285193.0
Split hands: 8047.0
Total amount bet: 4845795.0
Total initial bet: 4277895.0
Total net winnings: -18285.0
House edge: -0.4274298457535774
Element of risk: -0.37733746475036606


Player: Back Counter
--------------------
Total rounds played: 10297.0
Split hands: 270.0
Total amount bet: 2295305.0
Total initial bet: 2078735.0
Total net winnings: 82047.5
House edge: 3.946991800301626
Element of risk: 3.5745794131934536
```

## Figures

Setting `figures=True` in the [Setup Shoe Simulations](#setup-shoe-simulations) section creates a couple plots that help visualize our results.

![Card Counter Net Winnings](/documentation/net_winnings_card_counter.png?raw=true)
![Back Counter Net Winnings](/documentation/net_winnings_back_counter.png?raw=true)

The plots above are only created for players that count cards. The top sub-plot shows the net winnings per shoe for each hand played at a given running or true count for an individual player. The bottom sub-plot tracks the cumulative net winnings for an individual player as the running or true count increases.