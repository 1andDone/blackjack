class HouseRules:
    """
    Represents the rules at a table.

    """
    def __init__(
            self,
            min_bet: float | int,
            max_bet: float | int,
            s17: bool = True,
            blackjack_payout: float | int = 1.5,
            max_hands: int = 4,
            double_down: bool = True,
            split_unlike_tens: bool = False,
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
            True if dealer stands on a soft 17, false otherwise
        blackjack_payout
            Payout for a player receiving a natural blackjack (i.e. 3:2 is 1.5, 6:5 is 1.2)
        max_hands
            Maximum number of hands that a player can play at once after splitting
        double_down
            True if doubling is allowed on any first two cards, false otherwise
        split_unlike_tens
            True if able to split unlike 10's (i.e. J and Q), false otherwise
        double_after_split
            True if doubling after splits is allowed, false otherwise
        resplit_aces
            True if re-splitting aces is allowed, false otherwise
        insurance
            True if insurance bet is allowed, false otherwise
        late_surrender
            True if late surrender is allowed, false otherwise
        dealer_shows_hole_card
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
    def min_bet(self) -> float | int:
        return self._min_bet
    
    @property
    def max_bet(self) -> float | int:
        return self._max_bet
    
    @property
    def s17(self) -> bool:
        return self._s17
    
    @property
    def blackjack_payout(self) -> float | int:
        return self._blackjack_payout
    
    @property
    def max_hands(self) -> int:
        return self._max_hands
    
    @property
    def double_down(self) -> bool:
        return self._double_down
    
    @property
    def split_unlike_tens(self) -> bool:
        return self._split_unlike_tens
    
    @property
    def double_after_split(self) -> bool:
        return self._double_after_split
    
    @property
    def resplit_aces(self) -> bool:
        return self._resplit_aces
    
    @property
    def insurance(self) -> bool:
        return self._insurance
    
    @property
    def late_surrender(self) -> bool:
        return self._late_surrender
    
    @property
    def dealer_shows_hole_card(self) -> bool:
        return self._dealer_shows_hole_card