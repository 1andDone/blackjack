from house_rules import HouseRules
from player import Player
from play_shoe import PlayShoe


if __name__ == "__main__":

    # set table rules
    r = HouseRules(
                min_bet=5,
                max_bet=500,
                s17=True,
                blackjack_payout=1.5,
                max_hands=4,
                double_down=True,
                double_after_split=True,
                resplit_aces=False,
                insurance=True,
                late_surrender=True,
                dealer_shows_hole_card=False
    )

    # players that will be added to table
    p = [
            Player(
                name='Spotter',
                rules=r,
                bankroll=12000,
                min_bet=10,
                play_strategy='Basic',
                bet_strategy='Flat',
                count_strategy='Hi-Lo'),
            Player(
                name='Normal',
                rules=r,
                bankroll=755.75,
                min_bet=10,
                play_strategy='Basic',
                bet_strategy='Flat',
                count_strategy=None,
            ),
            Player(
                name='Big Money',
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
                back_counting_exit=1
            )
    ]

    # set up shoe simulation
    ps = PlayShoe(
            rules=r,
            players=p,
            seed=True,
            seed_number=78,
            simulations=15000,
            shoe_size=6,
            penetration=0.75,
            figures=True
    )

    ps.main()
