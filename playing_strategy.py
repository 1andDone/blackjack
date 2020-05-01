import basic_strategy


class PlayingStrategy(object):
    """
    PlayingStrategy is an object that represents the decisions a player will make when
    faced with a split situation or a certain soft/hard count. Decisions are typically based
    on whether or not a dealer stands or hits on a soft 17.

    """
    def __init__(self, rules, strategy):
        """
        Parameters
        ----------
        rules : HouseRules
            HouseRules class instance
        strategy : str
            Name of the playing strategy used by a player at the table
        """
        if strategy not in ['Basic']:
            raise ValueError('Strategy must be "Basic".')
        self.rules = rules
        self.strategy = strategy

    def get_strategy(self):
        return self.strategy

    def splits(self):
        if self.strategy == 'Basic' and self.rules.s17:
            return basic_strategy.s17_splits
        return basic_strategy.h17_splits

    def soft(self):
        if self.strategy == 'Basic' and self.rules.s17:
            return basic_strategy.s17_soft
        return basic_strategy.h17_soft

    def hard(self):
        if self.strategy == 'Basic' and self.rules.s17:
            return basic_strategy.s17_hard
        return basic_strategy.h17_hard
