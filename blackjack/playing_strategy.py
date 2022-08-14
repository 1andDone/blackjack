from blackjack.source.basic_strategy import s17_hard, s17_soft, s17_pair
from blackjack.source.basic_strategy import h17_hard, h17_soft, h17_pair


class PlayingStrategy:
    """
    Represents the decisions a player will make when faced with a
    pair split situation or a certain soft or hard count. Assumes the
    use of basic strategy.

    """
    def __init__(self, s17):
        """
        Parameters
        ----------
        s17: bool
            True if dealer stands on a soft 17, false otherwise
        
        """
        self._s17 = s17

    def hard(self, total, dealer_up_card):
        if self._s17:
            return s17_hard[total][dealer_up_card]
        return h17_hard[total][dealer_up_card]

    def soft(self, total, dealer_up_card):
        if self._s17:
            return s17_soft[total][dealer_up_card]
        return h17_soft[total][dealer_up_card]

    def pair(self, card, dealer_up_card):
        if self._s17:
            return s17_pair[card][dealer_up_card]
        return h17_pair[card][dealer_up_card]