class HouseRules:
    """
    Represents the rules at a table.

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
            not all players bust, surrender, or have natural 21, false otherwise
        
        """
        if min_bet <= 0:
            raise ValueError('Minimum bet at table must be greater than $0.')
        if max_bet <= min_bet:
            raise ValueError('Maximum bet at table must be greater than the minimum bet.')
        if blackjack_payout < 1:
            raise ValueError('Blackjack payout must be at least 1.')
        if max_hands < 2:
            raise ValueError('Maximum hands must be greater than or equal to 2.')
        if not double_down and double_after_split:
            raise ValueError("Cannot double after splitting if doubling down isn't allowed.")
        if resplit_aces and max_hands <= 2:
            raise ValueError('Max hands must be greater than 2 if re-splitting aces is allowed.')
        self._min_bet = min_bet
        self._max_bet = max_bet
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