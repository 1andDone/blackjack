# blackjack
Blackjack simulation between a dealer and player(s) where the user can change the house rules as well as the betting, playing, and card counting strategies for each player(s).

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

Additional parameters allows the user to specify the following:

- Minimum bet allowed at the table `min_bet`
- Maximum bet allowed at the table `max_bet`
- Dealer reveals hole card even when all players surrender, bust, or have natural blackjack `dealer_shows_hole_card`
    - This setting will only have an impact on players that are counting cards. By default, `dealer_shows_hole_card=False`.

An example of the *Vegas Strip* configuration is seen below:
```
r = HouseRules(
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
            dealer_shows_hole_card=False
)
```

## Setup Table

This simulation also allows the user to set betting, playing, and card counting strategies for individual players and have as many as 7 playing at a table at once. Individual players can have the following parameters:

- Name player is referred to at the table `name`
- Amount of money a player begins with when sitting down at the table `bankroll`
- Minimum amount of money a player is willing to wager when playing a hand `min_bet`
- Ratio of maximum bet to minimum bet `bet_spread`
- List of tuples where the first value of the tuple indicates the true count and the second value indicates the amount of money wagered for true counts closest to, but not equaling or exceeding, that particular true count. These values are used to create a bet scale with len(bet_count_amount) + 1 partitions, each incremented by the defined amount `bet_count_amount`
    - For example, if `min_bet=10`, `bet_strategy='Spread'` and `bet_spread=3`, setting `bet_count_amount=[(1, 10), (3, 15)]` would create three partitions - one for true counts less than 1 (player bets their personal minimum amount, $10), another for true counts greater than or equal to 1 and less than 3 (player bets $15), and finally, one for true counts greater than or equal to 3 (player bets $30, equivalent to `min_bet * bet_spread`).
- Playing strategy used by the player `play_strategy`
    - Currently, all players adhere to *Basic* strategy for playing decisions.
- Betting strategy used by the player `bet_strategy`
    - Options include *Flat*, where the player bets the same amount each hand, or *Spread*, where the player bets according to their bet scale.
- Card counting strategy used by the player, if any `count_strategy`
    - Options include balanced counting systems such as *Hi-Lo*, *Hi-Opt I*, *Hi-Opt II*, *Omega II*, *Halves*, and *Zen Count*.
- Indicates the level of accuracy to which a player can compute the true count (to the nearest 0.1, 0.5, or 1) `count_accuracy`
- Minimum true count at which a player will purchase insurance, if available `insurance_count`
- Strategy in which a player counts cards at a table but does not play a hand `back_counting` 
- List of true counts indicating the point at which a back counter will start and stop playing hands at the table `back_counting_entry_exit`

An example table setup is seen below:
```
p = [
        Player(
            name='Chris Counter',
            rules=r,
            bankroll=12000,
            min_bet=10,
            bet_spread=10,
            bet_count_amount=[(1, 10), (3, 50), (7, 75)],
            play_strategy='Basic',
            bet_strategy='Spread',
            count_strategy='Halves',
            insurance_count=5
        ),
        Player(
            name='Joe Average',
            rules=r,
            bankroll=750,
            min_bet=15,
            play_strategy='Basic',
            bet_strategy='Flat',
            count_strategy=None,
        ),
        Player(
            name='Benny Back Counter',
            rules=r,
            bankroll=50000,
            min_bet=25,
            bet_spread=12,
            bet_count_amount=[(1, 25), (3, 95), (5, 165), (10, 235)],
            play_strategy='Basic',
            bet_strategy='Spread',
            count_strategy='Hi-Lo',
            count_accuracy=0.1,
            back_counting=True,
            back_counting_entry_exit=[5, 0]
        )
]
```
In the example above, Chris Counter is the first to act every game and sits down at the table with a $12,000 bankroll. He will be counting cards using the Halves strategy and is able to compute the true count to the nearest 0.5. According to his bet scale, he will bet $10 (his personal minimum bet) for all true counts less than 1, $50 for all true counts greater than or equal to 1 and less than 5, $75 for all true counts greater than or equal to 5 and less than 7, and finally $100 (his personal maximum bet, according to his bet spread) for all true counts greater than or equal to 7. Additionally, Chris will make the insurance side bet offered at the table only when the true count is greater than or equal to 5.  

The next player to act, Joe Average, sits down at the table with $750 and will make $15 bets each hand. He does not bother counting cards.

Finally, the last player to act, Benny Back Counter, is back counting while using the Hi-Lo strategy. He only starts playing at the table when the true count (which he is able to compute to the nearest 0.1) is 5 or higher and will leave the table if it drops below 0. He starts off with $50,000 dollars and will bet a minimum of $25 each hand but is willing to bet up to $300 on any given hand, depending on the true count. The exact amount he bets is based on his personal betting scale where he bets $25 dollars for all true counts less than 1, $95 for all true counts greater than or equal to 1 but less than 3, $165 for all true counts greater than or equal to 3 but less than 5, $235 for all true counts greater than or equal to 5 but less than 10, and finally, $300 for all true counts greater than or equal to 10. 

## Setup Shoe Simulations

Now that the rules and table have been set, it's time to set up the shoe simulation. Below, a few important parameters are highlighted for the shoe simulation:

- Initializes the pseudorandom number generator to replicate the ordering of the deck from run-to-run `seed_number`
- Number of shoes to simulate over `simulations`
- Number of decks of cards that will be used in a shoe `shoe_size`
- Percentage of a shoe played before the shoe is re-shuffled `penetration`
- Option to create as many as three different visualizations for each player `figures`
    - See the [Figures](#figures) section for more information.

An example shoe simulation is seen below:
```
ps = PlayShoe(
        rules=r,
        players=p,
        seed_number=78,
        simulations=10000,
        shoe_size=6,
        penetration=0.75,
        figures=True
)
```

## Run 

Finally, after setting everything up, the code below runs the shoe simulation:
```
ps.main()
```

## Results

By default, basic shoe simulation statistics will be printed off. These include:

- *Total hands* - number of hands played by an individual player
- *Total amount bet* - combination of the initial wager and additional wagers from splits and doubling
- *Total initial bet* - only includes the initial wager (does not include additional wagers from splits and doubling)
- *Total net winnings* - total amount won by the player won less the total amount lost by the player 
- *House edge* - ratio of the total net winnings to the total initial bet
- *Element of risk* - ratio of the total net winnings to the total amount bet

```
Player: Chris Counter
---------------------
Total hands: 425189.0
Total amount bet: 11051057.5
Total initial bet: 9799185.0
Total net winnings: 55577.5
House edge: 0.5671645141917415
Element of risk: 0.5029156711925533


Player: Joe Average
-------------------
Total hands: 19463.0
Total amount bet: 322050.0
Total initial bet: 284025.0
Total net winnings: -750.0
House edge: -0.2640612622128334
Element of risk: -0.2328830926874709


Player: Benny Back Counter
--------------------------
Total hands: 22179.0
Total amount bet: 3355770.0
Total initial bet: 3026810.0
Total net winnings: 89015.0
House edge: 2.9408849580911918
Element of risk: 2.6525953804938958
```
In the example above, over the course of the simulation, Chris Counter won $55,577.50 while playing every hand of the simulation. Joe Average lasted 19,463 hands before having to leave the table after losing all of his initial bankroll. Benny Back Counter played slightly more hands than Joe Average but walked away with the most winnings, $89,015.

## Figures

Setting `figures=True` in the shoe simulation set up creates several plots that help visualize our results.

![Chris Counter Figure 1](/documentation/chris_counter_fig1.png?raw=true)
![Benny Back Counter Figure 1](/documentation/benny_back_counter_fig1.png?raw=true)

The two plots above are only created for players that count cards. These plots show the net winnings per shoe for each player for each hand played at a given true count. 

![Chris Counter Figure 2](/documentation/chris_counter_fig2.png?raw=true)
![Benny Back Counter Figure 2](/documentation/benny_back_counter_fig2.png?raw=true)

The two plots above are only created for players that count cards. These plots show the net cumulative net winnings per shoe for each player for each hand played at a given true count. 

![Chris Counter Figure 3](/documentation/chris_counter_fig3.png?raw=true)
![Joe Average Figure 3](/documentation/joe_average_fig3.png?raw=true)
![Benny Back Counter Figure 3](/documentation/benny_back_counter_fig3.png?raw=true)

The three plots above show the players bankroll growth over the course of the shoe simulations. 


