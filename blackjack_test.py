from house_rules import HouseRules
from player import Player
from play_shoe import PlayShoe

import time

start = time.time()

if __name__ == "__main__":

    # set table rules
    r = HouseRules(
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
                dealer_shows_hole_card=False
    )

    # players that will be added to table
    p = [
            Player(
                name='Average',
                rules=r,
                bankroll=1000000,
                min_bet=10,
                play_strategy='Basic',
                bet_strategy='Flat'
            )
    ]

    # set up shoe simulation
    ps = PlayShoe(
            rules=r,
            players=p,
            seed_number=78,
            simulations=10000,
            shoe_size=6,
            penetration=0.75,
            figures=True
    )

    ps.main()

end = time.time()

print('time elapsed:', end-start)