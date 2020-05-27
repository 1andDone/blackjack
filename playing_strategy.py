import basic_strategy
from house_rules import HouseRules


class PlayingStrategy(object):
    """
    PlayingStrategy is an object that represents the decisions a player will make when
    faced with a pair split situation or a certain soft/hard count. Decisions are based
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
        if not isinstance(rules, HouseRules):
            raise TypeError('Rules must be of type HouseRules.')
        if strategy != 'Basic':
            raise ValueError('Strategy must be "Basic".')
        self.rules = rules
        self._strategy = strategy

    @property
    def strategy(self):
        return self._strategy

    def pair(self):
        if self._strategy == 'Basic' and self.rules.s17:
            return basic_strategy.s17_pair
        return basic_strategy.h17_pair

    def soft(self):
        if self._strategy == 'Basic' and self.rules.s17:
            return basic_strategy.s17_soft
        return basic_strategy.h17_soft

    def hard(self):
        if self._strategy == 'Basic' and self.rules.s17:
            return basic_strategy.s17_hard
        return basic_strategy.h17_hard
