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
        if strategy not in ['Flat', 'Variable']:
            raise ValueError('Betting strategy must be either "Flat" or "Variable".')
        self.strategy = strategy

    def get_strategy(self):
        return self.strategy

    def initial_bet(self, min_bet, bet_spread, count=None, count_strategy=None):
        if self.strategy == 'Flat':
            return min_bet
        elif self.strategy == 'Variable':
            if count_strategy in ['Hi-Lo', 'Hi-Opt I', 'Hi-Opt II', 'Omega II', 'Halves', 'Zen Count']:
                if count < 1:
                    return min_bet
                elif count < 3:
                    return min_bet * (1 + (0.25 * (bet_spread - 1)))
                elif count < 5:
                    return min_bet * (1 + (0.5 * (bet_spread - 1)))
                elif count < 10:
                    return min_bet * (1 + (0.75 * (bet_spread - 1)))
                else:
                    return min_bet * bet_spread
            else:
                raise NotImplementedError('No implementation for this card counting strategy.')