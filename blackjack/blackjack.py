import random
from blackjack.dealer import Dealer
from blackjack.house_rules import HouseRules
from blackjack.shoe import Shoe
from blackjack.table import Table
from blackjack.helpers import play_round


class Blackjack:
    """
    Represents the simulation of one or more
    games of blackjack.
    
    """
    def __init__(
            self,
            min_bet,
            max_bet,
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
    ):
        """
        Parameters
        ----------
        min_bet: int
            Minimum bet allowed at the table
        max_bet: int
            Maximum bet allowed at the table
        s17: bool
            True if dealer stands on a soft 17, false otherwise
        blackjack_payout: float
            Payout for a player receiving a natural blackjack (i.e. 3:2 is 1.5, 6:5 is 1.2)
        max_hands: int
            Maximum number of hands that a player can play at once after splitting
        double_down: bool
            True if doubling is allowed on any first two cards, false otherwise
        split_unlike_tens: bool
            True if able to split unlike 10's (i.e. J and Q), false otherwise
        double_after_split: bool
            True if doubling after splits is allowed, false otherwise
        resplit_aces: bool
            True if re-splitting aces is allowed, false otherwise
        insurance: bool
            True if insurance bet is allowed, false otherwise
        late_surrender: bool
            True if late surrender is allowed, false otherwise
        dealer_shows_hole_card: bool
            True if the dealer shows his hole card regardless of whether or
            not all players bust, false otherwise
        
        """
        self._rules = HouseRules(
            min_bet=min_bet,
            max_bet=max_bet,
            s17=s17,
            blackjack_payout=blackjack_payout,
            max_hands=max_hands,
            double_down=double_down,
            split_unlike_tens=split_unlike_tens,
            double_after_split=double_after_split,
            resplit_aces=resplit_aces,
            insurance=insurance,
            late_surrender=late_surrender,
            dealer_shows_hole_card=dealer_shows_hole_card
        )
        self._table = Table(rules=self._rules)
        self._dealer = Dealer()
    
    def add_player(self, player):
        return self._table.add_player(player=player)
    
    def play_shoe(self, penetration, shoe_size):
        if penetration > 0.9:
            raise ValueError('Penetration must be less than or equal to 0.9')
        
        shoe = Shoe(shoe_size=shoe_size)
        shoe.shuffle()
        
        while not shoe.cut_card_reached(penetration=penetration) and self._table.players:
            play_round(table=self._table, dealer=self._dealer, rules=self._rules, shoe=shoe)
        
    def simulate(self, penetration, number_of_shoes, shoe_size, seed=None):
        if seed:
            random.seed(seed)
        
        for _ in range(number_of_shoes):
            if not self._table.players:
                break
            self.play_shoe(penetration=penetration, shoe_size=shoe_size)