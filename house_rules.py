class HouseRules(object):
    """
    HouseRules is an object where all of the table rules are set.

    """
    def __init__(
            self, min_bet, max_bet, s17=True, blackjack_payout=1.5, max_hands=4,
            double_down=True, split_unlike_tens=True, double_after_split=True, resplit_aces=False,
            insurance=True, late_surrender=True, dealer_shows_hole_card=False
    ):
        """
        Parameters
        ----------
        min_bet : int
            Minimum bet allowed at the table
        max_bet : int
            Maximum bet allowed at the table
        s17 : bool, optional
            True if dealer stands on a soft 17, false otherwise (default is True)
        blackjack_payout : float, optional
            Payout for a player receiving a natural blackjack (default is 1.5, which implies
            a 3:2 payout)
        max_hands : int, optional
            Maximum number of hands that a player can play (default is 4)
        double_down : bool, optional
            True if doubling is allowed on any first two cards, false otherwise (default is True)
        split_unlike_tens : bool, optional
            True if able to split unlike 10's (i.e. 'J' and 'Q'), false otherwise (default is True)
        double_after_split : bool, optional
            True if doubling after splits is allowed, false otherwise (default is True)
        resplit_aces : bool, optional
            True if re-splitting aces is allowed, false otherwise (default is False)
        insurance : bool, optional
            True if insurance bet is allowed, false otherwise (default is True)
        late_surrender : bool, optional
            True if late surrender is allowed, false otherwise (default is True)
        dealer_shows_hole_card : bool, optional
            True if the dealer shows his hole card regardless of whether or not all players bust,
            surrender, or have natural 21, false otherwise (default is False)
        """
        if min_bet < 0:
            raise ValueError('Minimum bet at table must be an integer greater than 0.')
        if max_bet < min_bet:
            raise ValueError('Maximum bet at table must be greater than minimum bet.')
        if max_hands not in [2, 3, 4]:
            raise ValueError('Maximum number of hands must be 2, 3, or 4.')
        if blackjack_payout <= 1:
            raise ValueError('Blackjack payout must be greater than 1.')
        self.min_bet = int(min_bet)
        self.max_bet = int(max_bet)
        self.s17 = s17
        self.blackjack_payout = float(blackjack_payout)
        self.max_hands = int(max_hands)
        self.double_down = double_down
        self.split_unlike_tens = split_unlike_tens
        self.double_after_split = double_after_split
        self.resplit_aces = resplit_aces
        self.insurance = insurance
        self.late_surrender = late_surrender
        self.dealer_shows_hole_card = dealer_shows_hole_card
