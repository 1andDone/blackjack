# blackjack
Blackjack simulation between player(s) and dealer.

![Blackjack](/documentation/blackjack.jpg?raw=true)

## Setup House Rules

This simulation allows the user to fully customize the house rules. By default, these are configured for the 'Vegas Strip' variant of blackjack which states that:

- Dealer stands on soft 17 `s17`
- Blackjack pays 3:2 `blackjack_payout`
- Players can split their hand 3 times, making up to 4 hands `max_hands`
- Players can double down on any two cards `double_down`
- Unlike 10-value cards may be split (i.e. 10-J) `split_unlike_tens`
- Players can double down after splitting `double_after_split`
- Aces can be split only once and players can only take one card to split Aces`resplit_aces`
- Players are allowed to surrender after dealer checks for blackjack and forfeit half their original wager `late_surrender`
- Insurance on a dealer Ace pays 2-1 `insurance`
- 21 on a split Ace does not count as Blackjack

An example of the 'Vegas Strip' configuration is seen below:
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

The user is also able to set the minimum (`min_bet`) and maximum (`max_bet`) allowed bet of the table. Additionally, only useful for card counting purposes, there is an option for the dealer to show their hole card (`dealer_shows_hole_card`) even when all players surrender, bust, or have natural 21. 

## Setup Table

This simulation allows the user to fully customize individual players and have as many as 7 playing at a table at once. All players adhere to basic strategy (`play_strategy`) for playing decisions and have the ability to count cards (`count_strategy`) using any of the following strategies: Hi-Lo, Hi-Opt I, Hi-Opt II, Omega II, Halves, or Zen Count. Additionally, if counting cards, players can be set up to back count (`back_counting`); that is, a player will only start playing at a table when they deem the count favorable (`back_counting_entry`) and will stop playing when the count is no longer favorable (`back_counting_exit`). Players betting strategies (`bet_strategy`) can also be customized. Players can be set up to either flat bet or place bets using a bet spread (`bet_spread`) that allows a player to vary their bet based on what they deem the count to be. 

An example table may look like this:
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
In the example above, Sarah Spotter is the first player at the table and thus, will be the first to act every game. She sits down at the table with a $12,000 bankroll and will bet the table minimum each hand. She is counting cards using the Hi-Lo method and is able to compute the current Hi-Lo true count to the nearest 0.5. The next player to act, Joe Average, sits down at the table with $750 and will make $15 bets each hand. He does not bother counting cards, as he's just playing for fun. Finally, the last player, Benny Big Money, is back counting while using the Hi-Lo method. He only starts playing at the table when the Hi-Lo true count is 5 or higher and will leave the table if it drops below 0. His brain is a calculator and he's able to compute the current Hi-Lo true count to the nearest 0.1. He starts off with $50,000 dollars and will bet a minimum of $25 each hand but is willing to bet anywhere from $25-$300 on any given hand, depending on the current Hi-Lo true count.

## Setup Shoe Simulations

Now that the rules and table have been set, it's time to set up the shoe simulation. In order to replicate results, a seed (`seed_number`) can be set. The number of simulations (`simulations`) determines the maximum number of shoes simulated. However, if all players lose their entire bankrolls, the simulation may end before the maximum number is reached. Other variables such as shoe size (`shoe_size`) and deck penetration (`penetration`) can be set as well. 

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

The code below runs the shoe simulation:
```
ps.main()
```

## Results

By default, basic shoe simulation statistics will be printed off.
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

From this example, we can see that Sarah Spotter lost a good portion of her original bankroll and Joe Average was forced to leave the table after losing all but $7.50 of his original bankroll. Benny Big Money only played 11,567 total hands but walked away $86,881.25 richer. 

## Figures

Setting `figures=True` in the shoe simulation set up creates a few plots that help visualize our results.

![Sarah Spotter Figure 1](/documentation/sarah_spotter_fig1.png?raw=true)
![Benny Big Money Figure 1](/documentation/benny_big_money_fig1.png?raw=true)

The two plots above show the net winnings per shoe for each hand played at a given Hi-Lo count. 

![Sarah Spotter Figure 2](/documentation/sarah_spotter_fig2.png?raw=true)
![Benny Big Money Figure 2](/documentation/benny_big_money_fig2.png?raw=true)

The two plots above show the net cumulative net winnings per shoe for each hand played at a given Hi-Lo count.

![Sarah Spotter Figure 3](/documentation/sarah_spotter_fig3.png?raw=true)
![Joe Average Figure 3](/documentation/joe_average_fig3.png?raw=true)
![Benny Big Money Figure 3](/documentation/benny_big_money_fig3.png?raw=true)

The three plots above show the bankroll growth over the course of the shoe simulations. 


