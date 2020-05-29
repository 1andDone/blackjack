from house_rules import HouseRules
from player import Player
from play_shoe import PlayShoe


if __name__ == "__main__":

    # set table rules
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

    # players that will be added to table
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

    # set up shoe simulation
    ps = PlayShoe(
            rules=r,
            players=p,
            seed_number=78,
            simulations=10000,
            penetration=0.75,
            figures=True
    )

    ps.main()

