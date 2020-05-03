# blackjack
Blackjack simulation between player(s) and dealer.

![Blackjack](/documentation/blackjack.jpg?raw=true)

## Setup House Rules

This simulation allows the user to fully customize the house rules. By default, these are configured for the *Vegas Strip* variant of blackjack which states that:

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

This simulations also allows the user to customize individual players and have as many as 7 playing at a table at once. Individual players can have the following properties:

- Unique word or set of words a player is referred to as `name`
- Amount of money a player starts out with when sitting down at a table `bankroll`
- Minimum amount of money a player is willing to wager when playing a hand `min_bet`
- Ratio of maximum bet to minimum bet `bet_spread`
- Playing strategy used by the player `play_strategy`
    - All players adhere to *Basic* strategy for playing decisions
- Betting strategy used by the player `bet_strategy`
    - Options include *Flat* or *Variable*
- Card counting strategy used by the player, if any `count_strategy`
<<<<<<< HEAD
    - Options include strategies that rely on running counts (*Hi-Opt I*, *Hi-Opt II*) as well as true counts (*Hi-Lo*, *Omega II*, *Halves*, or *Zen Count*)
- Accuracy of the true count `count_accuracy`
   - Indicates that a player can compute the true count to the nearest *0.1*, *0.5*, or *1* 
=======
    - Options include balanced counting systems such as *Hi-Lo*, *Hi-Opt I*, *Hi-Opt II*, *Omega II*, *Halves*, and *Zen Count*
- Accuracy of the running or true count `count_accuracy`
   - Indicates that a player can compute the running or true count to the nearest *0.1*, *0.5*, or *1* 
>>>>>>> 7409e8a5128c566e79756c5d2c2fd8d1b9dbaf79
- Strategy in which a player continues to count cards but does not play a hand `back_counting` 
- Count at which the back counter will start playing hands at the table `back_counting_entry`
- Count at which the back counter will stop playing hands at the table `back_counting_exit`

An example table setup is seen below:
```
p = [
        Player(
            name='Sarah Spotter',
            rules=r,
            bankroll=12000,
            min_bet=10,
            play_strategy='Basic',
            bet_strategy='Flat',
            count_strategy='Hi-Lo',
            count_accuracy=0.5),
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
            name='Benny Big Money',
            rules=r,
            bankroll=50000,
            min_bet=25,
            bet_spread=12,
            play_strategy='Basic',
            bet_strategy='Variable',
            count_strategy='Hi-Lo',
            count_accuracy=0.1,
            back_counting=True,
            back_counting_entry=5,
            back_counting_exit=0
        )
]
```
In the example above, Sarah Spotter will be the first to act every game. She sits down at the table with a $12,000 bankroll and will bet the table minimum ($10) each hand. She is counting cards using the Hi-Lo strategy and is able to compute the true count to the nearest 0.5. The next player to act, Joe Average, sits down at the table with $750 and will make $15 bets each hand. He does not bother counting cards, as he's just playing for fun. Finally, the last player, Benny Big Money, is back counting while using the Hi-Lo strategy. He only starts playing at the table when the Hi-Lo true count is 5 or higher and will leave the table if it drops below 0. His brain is a calculator and he's able to compute the current true count to the nearest 0.1. He starts off with $50,000 dollars and will bet a minimum of $25 each hand but is willing to bet up to $300 on any given hand, depending on the Hi-Lo true count.

## Setup Shoe Simulations

Now that the rules and table have been set, it's time to set up the shoe simulation. Below, a few important parameters are highlighted for the shoe simulation:

- Initialize the pseudorandom number generator in Python to replicate results from run-to-run `seed_number`
- Number of shoes to simulate over `simulations`
- Number of decks of cards that will be used in a shoe `shoe_size`
- Percentage of shoe played before the shoe is re-shuffled `penetration`

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

- **Total hands** - number of hands played by an individual player
- **Total amount bet** - combination of the initial wager and additional wagers from splits and doubling
- **Total initial bet** - only includes the initial wager (does not include additional wagers from splits and doubling)
- **Total net winnings** - total amount won by the player won less the total amount lost by the player 
- **House edge** - ratio of the total net winnings to the total initial bet
- **Element of risk** - ratio of the total net winnings to the total amount bet

```
Player: Sarah Spotter
---------------------
Total hands: 431303.0
Total amount bet: 4750430.0
Total initial bet: 4195060.0
Total net winnings: -8515.0
House edge: -0.20297683465790714
Element of risk: -0.17924693133042693


Player: Joe Average
-------------------
Total hands: 18097.0
Total amount bet: 298980.0
Total initial bet: 264315.0
Total net winnings: -742.5
House edge: -0.2809148175472448
Element of risk: -0.24834437086092717


Player: Benny Big Money
-----------------------
Total hands: 11567.0
Total amount bet: 2562887.5
Total initial bet: 2324962.5
Total net winnings: 86881.25
House edge: 3.7368882293800434
Element of risk: 3.3899751744858095
```
In the example above, over the course of the simulation, Sarah Spotter lost a good portion of her original bankroll while playing every hand of simulation. Joe Average lasted 18,097 hands before having to leave the table after losing all but $7.50 of his initial bankroll. Benny Big Money played the least amount of hands among the players but walked away $86,881.25 richer. 

## Figures

Setting `figures=True` in the shoe simulation set up creates a few plots that help visualize our results.

![Sarah Spotter Figure 1](/documentation/sarah_spotter_fig1.png?raw=true)
![Benny Big Money Figure 1](/documentation/benny_big_money_fig1.png?raw=true)

The two plots above are only created for players that are counting cards and show the net winnings per shoe for each hand played at a given true count. 

![Sarah Spotter Figure 2](/documentation/sarah_spotter_fig2.png?raw=true)
![Benny Big Money Figure 2](/documentation/benny_big_money_fig2.png?raw=true)

The two plots above are only created for players that are counting cards and show the net cumulative net winnings per shoe for each hand played at a given true count. 

![Sarah Spotter Figure 3](/documentation/sarah_spotter_fig3.png?raw=true)
![Joe Average Figure 3](/documentation/joe_average_fig3.png?raw=true)
![Benny Big Money Figure 3](/documentation/benny_big_money_fig3.png?raw=true)

The three plots above show the bankroll growth over the course of the shoe simulations. 


