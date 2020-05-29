class HouseRules(object):
    """
    HouseRules is an object where all of the table rules are set.

    """
    def __init__(
            self, shoe_size, bet_limits, s17=True, blackjack_payout=1.5, max_hands=4,
            double_down=True, split_unlike_tens=True, double_after_split=True,
            resplit_aces=False, insurance=True, late_surrender=True, dealer_shows_hole_card=False
    ):
        """
        Parameters
        ----------
        shoe_size: int
            Number of decks used during a blackjack game
        bet_limits : list
            List containing the minimum and maximum bet allowed at the table
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
        if shoe_size not in [4, 6, 8]:
            raise ValueError('Shoe size must be 4, 6, or 8.')
        if len(bet_limits) != 2:
            raise ValueError('Bet limits should be a list of 2 integers.')
        if not all(isinstance(bet, int) for bet in bet_limits):
            raise TypeError('Bet limits need to be integer values.')
        if bet_limits[0] < 0:
            raise ValueError('Minimum bet at table must be an integer greater than 0.')
        if bet_limits[1] <= bet_limits[0]:
            raise ValueError('Maximum bet at table must be greater than minimum bet.')
        if blackjack_payout <= 1:
            raise ValueError('Blackjack payout must be greater than 1.')
        if max_hands not in [2, 3, 4]:
            raise ValueError('Maximum number of hands must be 2, 3, or 4.')
        if resplit_aces and max_hands == 2:
            raise ValueError('Max hands must be greater than 2 if re-splitting aces is allowed.')
        self._shoe_size = shoe_size
        self._min_bet = bet_limits[0]
        self._max_bet = bet_limits[1]
        self._s17 = s17
        self._blackjack_payout = blackjack_payout
        self._max_hands = max_hands
        self._double_down = double_down
        self._split_unlike_tens = split_unlike_tens
        self._double_after_split = double_after_split
        self._resplit_aces = resplit_aces
        self._insurance = insurance
        self._late_surrender = late_surrender
        self._dealer_shows_hole_card = dealer_shows_hole_card

    def __str__(self):
        return '{shoe_size} decks,{s17} {blackjack_payout}{double_after_split}{resplit_aces}{late_surrender}'.format(
                shoe_size=self._shoe_size,
                s17=' S17,' if self._s17 else 'H17,',
                blackjack_payout=str(self._blackjack_payout) + 'x BJ,',
                double_after_split=' DAS,' if self._double_after_split else '',
                resplit_aces=' RSA,' if self._resplit_aces else '',
                late_surrender=' LS' if self._late_surrender else ''
        )

    @property
    def shoe_size(self):
        return self._shoe_size

    @property
    def min_bet(self):
        return self._min_bet

    @property
    def max_bet(self):
        return self._max_bet

    @property
    def s17(self):
        return self._s17

    @property
    def blackjack_payout(self):
        return self._blackjack_payout

    @property
    def max_hands(self):
        return self._max_hands

    @property
    def double_down(self):
        return self._double_down

    @property
    def split_unlike_tens(self):
        return self._split_unlike_tens

    @property
    def double_after_split(self):
        return self._double_after_split

    @property
    def resplit_aces(self):
        return self._resplit_aces

    @property
    def insurance(self):
        return self._insurance

    @property
    def late_surrender(self):
        return self._late_surrender

    @property
    def dealer_shows_hole_card(self):
        return self._dealer_shows_hole_card
