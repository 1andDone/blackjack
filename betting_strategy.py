class BettingStrategy(object):
    """
    BettingStrategy is a class that determines the betting strategy used by
    a player at the table.

    """
    def __init__(self, strategy):
        """
        Parameters
        ----------
        strategy : str
            Name of the betting strategy used by a player at the table
        """
        if strategy not in ['Flat', 'Spread']:
            raise ValueError('Betting strategy must be either "Flat" or "Spread".')
        self.strategy = strategy

    def get_strategy(self):
        return self.strategy

    def initial_bet(self, min_bet, bet_spread, bet_scale=None, count=None):
        if self.strategy == 'Flat':
            return min_bet
        else:
            amount = bet_spread * min_bet
            for key, value in bet_scale.items():
                if count < key:
                    amount = value
                    break
            return amount
