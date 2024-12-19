import random
from blackjack.dealer import Dealer
from blackjack.house_rules import HouseRules
from blackjack.player import Player
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
        min_bet: int,
        max_bet: int,
        s17: bool = True,
        blackjack_payout: int | float = 1.5,
        max_hands: int = 4,
        double_down: bool = True,
        double_after_split: bool = False,
        resplit_aces: bool = False,
        insurance: bool = True,
        late_surrender: bool = True,
        dealer_shows_hole_card: bool = False
    ):
        """
        Parameters
        ----------
        min_bet
            Minimum bet allowed at the table
        max_bet
            Maximum bet allowed at the table
        s17
            True if dealer stands on a soft 17, False otherwise
        blackjack_payout
            Payout for a player receiving a natural blackjack (i.e. 3:2 is 1.5, 6:5 is 1.2)
        max_hands
            Maximum number of hands that a player can play at once after splitting
        double_down
            True if doubling is allowed on any first two cards, False otherwise
        split_unlike_tens
            True if able to split unlike 10's (i.e. J and Q), False otherwise
        double_after_split
            True if doubling after splits is allowed, False otherwise
        resplit_aces
            True if re-splitting aces is allowed, False otherwise
        insurance
            True if insurance bet is allowed, False otherwise
        late_surrender
            True if late surrender is allowed, False otherwise
        dealer_shows_hole_card
            True if the dealer shows his hole card regardless of whether or
            not all players bust, False otherwise

        """
        self._rules = HouseRules(
            min_bet=min_bet,
            max_bet=max_bet,
            s17=s17,
            blackjack_payout=blackjack_payout,
            max_hands=max_hands,
            double_down=double_down,
            double_after_split=double_after_split,
            resplit_aces=resplit_aces,
            insurance=insurance,
            late_surrender=late_surrender,
            dealer_shows_hole_card=dealer_shows_hole_card
        )
        self._table = Table(rules=self._rules)
        self._dealer = Dealer()

    def add_player(self, player: Player) -> None:
        return self._table.add_player(player=player)

    def play_shoe(self, penetration: float, shoe_size: int) -> None:
        if penetration > 0.9:
            raise ValueError('Penetration must be less than or equal to 0.9')

        shoe = Shoe(shoe_size=shoe_size)
        shoe.shuffle()

        while not shoe.cut_card_reached(penetration=penetration) and self._table.players:
            play_round(table=self._table, dealer=self._dealer, rules=self._rules, shoe=shoe)

    def simulate(self, penetration: float, number_of_shoes: int, shoe_size: int, seed: int | None = None) -> None:
        if seed:
            random.seed(seed)

        for _ in range(number_of_shoes):
            if not self._table.players:
                break
            self.play_shoe(penetration=penetration, shoe_size=shoe_size)
