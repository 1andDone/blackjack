from math import ceil, floor
from blackjack import Player, CountingStrategy


class CardCounter(Player):
    """
    Represents an individual player at a table that
    counts cards according to a counting strategy.
    
    """
    def __init__(self, counting_strategy, bet_ramp, insurance=None, **kwargs):
        """
        Parameters
        ----------
        counting_strategy: CountingStrategy
            Card counting strategy used by the player
        bet_ramp: dict
            Dictionary where each key value is the running or
            true count and each value indicates the amount of money
            wagered at that running or true count
        insurance: int or float
            Minimum running or true count at which a player will
            purchase insurance, if desired, and if available
        
        """
        super().__init__(**kwargs)
        self.max_bet_ramp = max(bet for _, bet in bet_ramp.items())

        if self.max_bet_ramp > self.bankroll:
            raise ValueError('Maximum bet in the "bet_ramp" exceeds the bankroll.')
        
        self.min_bet_ramp = min(bet for _, bet in bet_ramp.items())
        self.min_count = min(count for count, _ in bet_ramp.items())
        self.max_count = max(count for count, _ in bet_ramp.items())
        
        counts_to_check = [count for count in range(ceil(self.min_count), floor(self.max_count) + 1)]
        if counting_strategy == CountingStrategy.HALVES:
            counts_to_check.extend([count + 0.5 for count in range(floor(self.min_count), floor(self.max_count))])
        
        for count in counts_to_check:
            try:
                bet_ramp[count]
            except:
                raise KeyError('Count does not exist in "bet_ramp".')

        self._bet_ramp = bet_ramp
        self._counting_strategy = counting_strategy
        self._insurance = insurance
    
    @property
    def counting_strategy(self):
        return self._counting_strategy
    
    def initial_wager(self, count):
        if count < self.min_count:
            return self._min_bet
        elif count >= self.max_count:
            return self.max_bet_ramp
        else:
            return self._bet_ramp[count]

    @property
    def insurance(self):
        return self._insurance